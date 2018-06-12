import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect
from oic import rndstr
from oic.oauth2 import AuthorizationResponse, ResponseError

from apps.dataporten.study.tasks import fetch_groups_information, find_user_study_and_update

from .client import client_setup

logger = logging.getLogger(__name__)

DATAPORTEN_CLIENT_ID = settings.DATAPORTEN.get('STUDY', {}).get('CLIENT_ID')
DATAPORTEN_CLIENT_SECRET = settings.DATAPORTEN.get('STUDY', {}).get('CLIENT_SECRET')
DATAPORTEN_REDIRECT_URI = settings.DATAPORTEN.get('STUDY', {}).get('REDIRECT_URI')
DATAPORTEN_SCOPES = settings.DATAPORTEN.get('STUDY', {}).get('SCOPES')


@login_required()
def study(request):
    """This view redirects the user to Dataporten to request authorization for fetching information about the
    user's groups membership, which can be used to verify eligibility for membership of Online."""
    if request.user.is_member:
        messages.info(request, 'Du er allerede registrert som medlem.')
        return redirect('profiles_active', active_tab='membership')

    logger.debug(
        '{} wants to automatically confirm study programme through Dataporten.'.format(request.user),
        extra={'user': request.user}
    )

    client = client_setup(DATAPORTEN_CLIENT_ID, DATAPORTEN_CLIENT_SECRET)

    # Generate random values used to verify that it's the same user when in the callback.
    state = rndstr()
    nonce = rndstr()

    request.session['dataporten_study_state'] = state
    request.session['dataporten_study_nonce'] = nonce

    args = {
        'client_id': DATAPORTEN_CLIENT_ID,
        'response_type': 'code',
        'scope': DATAPORTEN_SCOPES,
        'redirect_uri': DATAPORTEN_REDIRECT_URI,
        'nonce': nonce,
        'state': state,
    }

    logger.debug(
        'Constructing authorization request and redirecting user to authorize through Dataporten.',
        extra={'user': request.user}
    )

    auth_req = client.construct_AuthorizationRequest(request_args=args)
    login_url = auth_req.request(client.authorization_endpoint)

    return redirect(login_url)


@login_required()
def study_callback(request):
    """This view fetches information from Dataporten to verify the eligibility. This is done by fetching
    the /me/groups-API from Dataporten and further processing the fetched groups to find group membership.

    Dataporten Groups API: https://docs.dataporten.no/docs/groups/"""
    logger.debug('Fetching study programme for user {}'.format(request.user), extra={'user': request.user})

    client = client_setup(DATAPORTEN_CLIENT_ID, DATAPORTEN_CLIENT_SECRET)

    queryparams = request.GET.urlencode()

    try:
        auth_resp = client.parse_response(AuthorizationResponse, info=queryparams, sformat='urlencoded')
    except ResponseError:
        messages.error(request, 'Forespørselen mangler påkrevde felter, vennligst prøv igjen.')
        return redirect('profiles_active', active_tab='membership')

    if not request.session.get('dataporten_study_state', '') or \
            request.session['dataporten_study_state'] != auth_resp['state']:
        logger.warning('Dataporten state did not equal the one in session!')
        messages.error(request, 'Verifisering av forespørselen feilet. Vennligst prøv igjen.')
        return redirect('profiles_active', active_tab='membership')

    args = {
        'code': auth_resp['code'],
        'redirect_uri': DATAPORTEN_REDIRECT_URI,
    }

    token_request = client.do_access_token_request(
        state=auth_resp['state'], request_args=args, authn_method='client_secret_basic',
    )

    access_token = token_request.get('access_token')

    # Do user info request
    userinfo = client.do_user_info_request(state=auth_resp['state'], behavior='use_authorization_header')
    ntnu_username_dataporten = userinfo.get('email').split('@')[0]
    if request.user.ntnu_username and request.user.ntnu_username != ntnu_username_dataporten:
        logger.warning(
            '{} tried to authorize, but the registered ntnu_username and the one received from Dataporten differ.'
            .format(request.user),
            extra={
                'user': request.user,
                'ntnu_username__ow4': request.user.ntnu_username,
                'ntnu_username__dataporten': ntnu_username_dataporten
            }
        )
        messages.error(
            request,
            'Brukernavnet for brukerkontoen brukt til verifisering i Dataporten stemmer ikke overens med '
            'kontoen du er logget inn med hos Online. Pass på at du er logget inn på din egen konto begge '
            'steder og prøv igjen.'
        )
        return redirect('profiles_active', active_tab='membership')
    elif not request.user.ntnu_username:
        pass  # @ToDo: Register email address. Maybe store it, but ask user to confirm? -> resend auth email

    # Getting information about study of the user
    groups = fetch_groups_information(access_token)

    try:
        studies_informatics = find_user_study_and_update(request.user, groups)
    except IntegrityError:
        messages.error(
            request,
            'En bruker er allerede knyttet til denne NTNU-kontoen. '
            'Dersom du har glemt passordet til din andre bruker kan du bruke "glemt passord"-funksjonen.'
        )
        return redirect('profiles_active', active_tab='membership')

    if studies_informatics:
        messages.success(
            request,
            'Bekreftet studieretning som {} i {}. klasse. Dersom dette er feil, '
            'kontakt dotkom slik at vi kan rette opp og finne ut hva som gikk galt.'
            .format(request.user.get_field_of_study_display(), request.user.year)
        )
    else:
        messages.error(
            request,
            'Det ser ikke ut som du tar informatikkfag. Dersom du mener dette er galt kan du sende inn en søknad '
            'manuelt. Ta gjerne kontakt med dotkom slik at vi kan feilsøke prosessen.'
        )

    return redirect('profiles_active', active_tab='membership')
