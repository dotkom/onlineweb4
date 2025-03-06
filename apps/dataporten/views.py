import logging
from urllib.parse import urlparse

import requests
import sentry_sdk
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect
from oic import rndstr
from oic.oauth2 import AuthorizationResponse, ResponseError

from apps.authentication.auth0 import auth0_client
from apps.authentication.models import OnlineUser
from apps.dataporten.study.tasks import (
    fetch_groups_information,
    find_user_study_and_update,
)

from .client import client_setup

logger = logging.getLogger(__name__)

DATAPORTEN_CLIENT_ID = settings.DATAPORTEN.get("STUDY", {}).get("CLIENT_ID")
DATAPORTEN_CLIENT_SECRET = settings.DATAPORTEN.get("STUDY", {}).get("CLIENT_SECRET")
DATAPORTEN_REDIRECT_URI = settings.DATAPORTEN.get("STUDY", {}).get("REDIRECT_URI")
DATAPORTEN_SCOPES = settings.DATAPORTEN.get("STUDY", {}).get("SCOPES")


@login_required()
def study(request):
    """This view redirects the user to Dataporten to request authorization for fetching information about the
    user's groups membership, which can be used to verify eligibility for membership of Online.
    """

    logger.debug(
        f"{request.user} wants to automatically confirm study programme through Dataporten.",
        extra={"user": request.user},
    )

    client = client_setup(DATAPORTEN_CLIENT_ID, DATAPORTEN_CLIENT_SECRET)

    # Generate random values used to verify that it's the same user when in the callback.
    state = rndstr()
    nonce = rndstr()

    request.session["dataporten_study_state"] = state
    request.session["dataporten_study_nonce"] = nonce

    # Save referer to see if the request should redirect to old or OWF on callback.
    request.session["dataporten_study_referer"] = request.META["HTTP_REFERER"]

    args = {
        "client_id": DATAPORTEN_CLIENT_ID,
        "response_type": "code",
        "scope": DATAPORTEN_SCOPES,
        "redirect_uri": DATAPORTEN_REDIRECT_URI,
        "nonce": nonce,
        "state": state,
    }

    logger.debug(
        "Constructing authorization request and redirecting user to authorize through Dataporten.",
        extra={"user": request.user},
    )

    auth_req = client.construct_AuthorizationRequest(request_args=args)
    login_url = auth_req.request(client.authorization_endpoint)

    return redirect(login_url)


@login_required()
def study_callback(request):  # noqa: C901
    """This view fetches information from Dataporten to verify the eligibility. This is done by fetching
    the /me/groups-API from Dataporten and further processing the fetched groups to find group membership.

    Dataporten Groups API: https://docs.dataporten.no/docs/groups/"""
    logger.debug(
        f"Fetching study programme for user {request.user}",
        extra={"user": request.user},
    )
    client = client_setup(DATAPORTEN_CLIENT_ID, DATAPORTEN_CLIENT_SECRET)

    queryparams = request.GET.urlencode()

    try:
        auth_resp = client.parse_response(
            AuthorizationResponse, info=queryparams, sformat="urlencoded"
        )
    except ResponseError:
        messages.error(
            request, "Forespørselen mangler påkrevde felter, vennligst prøv igjen."
        )
        return redirect("profiles_active", active_tab="membership")

    if (
        not request.session.get("dataporten_study_state", "")
        or request.session["dataporten_study_state"] != auth_resp["state"]
    ):
        logger.warning("Dataporten state did not equal the one in session!")
        messages.error(
            request, "Verifisering av forespørselen feilet. Vennligst prøv igjen."
        )
        return redirect("profiles_active", active_tab="membership")

    args = {"code": auth_resp["code"], "redirect_uri": DATAPORTEN_REDIRECT_URI}

    token_request = client.do_access_token_request(
        state=auth_resp["state"], request_args=args, authn_method="client_secret_basic"
    )

    access_token = token_request.get("access_token")

    # Do user info request
    userinfo = client.do_user_info_request(
        state=auth_resp["state"], behavior="use_authorization_header"
    )
    # connect-userid_sec format is array with "feide:username@ntnu.no"
    ntnu_username_dataporten = (
        userinfo.get("connect-userid_sec")[0].split(":")[1].split("@")[0]
    )
    if (
        request.user.ntnu_username
        and request.user.ntnu_username != ntnu_username_dataporten
    ):
        logger.warning(
            f"{request.user} tried to authorize, but the registered ntnu_username and the one received from Dataporten differ.",
            extra={
                "user": request.user,
                "ntnu_username__ow4": request.user.ntnu_username,
                "ntnu_username__dataporten": ntnu_username_dataporten,
            },
        )
        messages.error(
            request,
            "Brukernavnet for brukerkontoen brukt til verifisering i Dataporten stemmer ikke overens med "
            "kontoen du er logget inn med hos Online. Pass på at du er logget inn på din egen konto begge "
            "steder og prøv igjen.",
        )
        return redirect("profiles_active", active_tab="membership")
    elif not request.user.ntnu_username:
        auth0 = auth0_client()
        conflicting_users = auth0.users.list(
            q=f"app_metadata.ntnu_username:{ntnu_username_dataporten}"
        )
        if len(conflicting_users["users"]) != 0:
            sentry_sdk.capture_message(
                f"Dataporten user already exists in Auth0 {ntnu_username_dataporten}"
            )
            messages.error(
                request,
                "Noe gikk galt, prøv igjen senere eller kontakt dotkom.",
            )
            return redirect("profiles_active", active_tab="membership")

        # @ToDo: Register email address. Maybe store it, but ask user to confirm? -> resend auth email

    try:
        extended_userinfo = requests.get(
            "https://api.dataporten.no/userinfo/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        messages.error(
            request,
            "Noe gikk galt, prøv igjen senere eller kontakt dotkom.",
        )
        return redirect("profiles_active", active_tab="membership")

    # Getting information about study of the user
    groups = fetch_groups_information(access_token)

    try:
        given_name = extended_userinfo["givenName"][0]
        family_name = extended_userinfo["sn"][0]
        user: OnlineUser = request.user
        user.ntnu_username = ntnu_username_dataporten
        user.first_name = given_name
        user.last_name = family_name
        user.save()
        studies_info = find_user_study_and_update(request.user, groups)

        if not studies_info:
            logger.warning(
                "Dataporten groups do not match groups for informatics",
                extra={"user": request.user, "groups": groups},
            )
            messages.error(
                request,
                "Studieretningen du studerer ved gir ikke medlemskap i Online. ",
                "Hvis du mener dette er en feil; ta vennligst kontakt dotkom slik at vi kan feilsøke prosessen.",
            )
            return redirect("profiles_active", active_tab="membership")

        studies_informatics, study_name, study_year = studies_info
    except IntegrityError:
        messages.error(
            request,
            "En bruker er allerede knyttet til denne NTNU-kontoen. "
            'Dersom du har glemt passordet til din andre bruker kan du bruke "glemt passord"-funksjonen.',
        )
        return redirect("profiles_active", active_tab="membership")

    if studies_informatics:
        messages.success(
            request,
            f"Bekreftet studieretning som {study_name} i {study_year}. klasse. Dersom dette er feil, "
            "søk om medlemskap med manuell godkjenning eller kontakt dotkom slik at vi kan rette opp.",
        )
    else:
        messages.error(
            request,
            "Det ser ikke ut som du tar informatikkfag. Dersom du mener dette er galt kan du sende inn en søknad "
            "manuelt. Ta gjerne kontakt med dotkom slik at vi kan feilsøke prosessen.",
        )

    # If the request came from OWF, redirect there.
    if request.session["dataporten_study_referer"]:
        host = urlparse(request.session["dataporten_study_referer"])
        if host and host.hostname and host.hostname.endswith("online.ntnu.no"):
            return redirect("https://online.ntnu.no/profile/settings/membership")

    return redirect("profiles_active", active_tab="membership")
