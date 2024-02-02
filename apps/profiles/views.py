# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from googleapiclient.errors import HttpError
from rest_framework import filters, mixins, permissions, response, viewsets
from watson import search as watson

from apps.approval.forms import FieldOfStudyApplicationForm
from apps.approval.models import MembershipApproval
from apps.authentication.constants import GroupType
from apps.authentication.models import Email, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position
from apps.authentication.serializers import EmailReadOnlySerializer
from apps.dashboard.tools import has_access
from apps.gsuite.accounts.main import (
    create_g_suite_account,
    reset_password_g_suite_account,
)
from apps.marks.models import Mark, MarkRuleSet, Suspension
from apps.payment.models import PaymentDelay, PaymentRelation, PaymentTransaction
from apps.profiles.filters import PublicProfileFilter
from apps.profiles.forms import PositionForm, PrivacyForm, ProfileForm
from apps.profiles.models import Privacy
from apps.profiles.serializers import (
    PrivacySerializer,
    ProfileSerializer,
    PublicProfileSerializer,
)
from apps.shop.models import Order
from utils.shortcuts import render_json

"""
Index for the entire user profile view
Methods redirect to this view on save
"""


@login_required
def index(request, active_tab="overview"):
    context = _create_profile_context(request)
    context["active_tab"] = active_tab

    return render(request, "profiles/index.html", context)


def _create_profile_context(request):
    groups = Group.objects.all()

    Privacy.objects.get_or_create(user=request.user)  # This is a hack
    """
    To make sure a privacy exists when visiting /profiles/privacy/.
    Until now, it has been generated upon loading models.py, which is a bit hacky.
    The code is refactored to use Django signals, so whenever a user is created, a privacy-property is set up.
    """

    context = {
        # edit
        "position_form": PositionForm(),
        "user_profile_form": ProfileForm(instance=request.user),
        # positions
        "groups": groups,
        # privacy
        "privacy_form": PrivacyForm(instance=request.user.privacy),
        # nibble information
        "transactions": PaymentTransaction.objects.filter(user=request.user),
        "orders": Order.objects.filter(order_line__user=request.user).order_by(
            "-order_line__datetime"
        ),
        # marks
        "mark_rule_set": MarkRuleSet.get_current_rule_set(),
        "mark_rules_accepted": request.user.mark_rules_accepted,
        "marks": [
            # Tuple syntax ('title', list_of_marks, is_collapsed)
            (_("aktive prikker"), Mark.marks.active(request.user), False),
            (_("inaktive prikker"), Mark.marks.inactive(request.user), True),
        ],
        "suspensions": [
            # Tuple syntax ('title', list_of_marks, is_collapsed)
            (
                _("aktive suspensjoner"),
                Suspension.objects.filter(user=request.user, active=True),
                False,
            ),
            (
                _("inaktive suspensjoner"),
                Suspension.objects.filter(user=request.user, active=False),
                True,
            ),
        ],
        # approvals
        "field_of_study_application": FieldOfStudyApplicationForm(),
        "has_active_approvals": MembershipApproval.objects.filter(
            applicant=request.user, processed=False
        ).count()
        > 0,
        "approvals": [
            # Tuple syntax ('title', list_of_approvals, is_collapsed)
            (
                _("aktive søknader"),
                MembershipApproval.objects.filter(
                    applicant=request.user, processed=False
                ),
                False,
            ),
            (
                _("avslåtte søknader"),
                MembershipApproval.objects.filter(
                    applicant=request.user, processed=True, approved=False
                ),
                True,
            ),
            (
                _("godkjente søknader"),
                MembershipApproval.objects.filter(
                    applicant=request.user, processed=True
                ),
                True,
            ),
        ],
        "payments": [
            (
                _("ubetalt"),
                PaymentDelay.objects.all().filter(user=request.user, active=True),
                False,
            ),
            (
                _("betalt"),
                PaymentRelation.objects.all().filter(user=request.user),
                True,
            ),
        ],
        "in_comittee": has_access(request),
        "DATAPORTEN_ENABLED": "apps.dataporten" in settings.INSTALLED_APPS,
    }

    return context


@login_required
def edit_profile(request):
    context = _create_profile_context(request)
    context["active_tab"] = "edit"

    if request.method == "POST":
        user_profile_form = ProfileForm(request.POST, instance=request.user)
        context["user_profile_form"] = user_profile_form

        if not user_profile_form.is_valid():
            messages.error(request, _("Noen av de påkrevde feltene mangler"))
        else:
            user_profile_form.save()
            messages.success(request, _("Brukerprofilen din ble endret"))

    return render(request, "profiles/index.html", context)


@login_required
def privacy(request):
    context = _create_profile_context(request)
    context["active_tab"] = "privacy"

    if request.method == "POST":
        privacy_form = PrivacyForm(request.POST, instance=request.user.privacy)
        context["privacy_form"] = privacy_form

        if not privacy_form.is_valid():
            messages.error(request, _("Noen av de påkrevde feltene mangler"))
        else:
            privacy_form.save()
            messages.success(request, _("Personvern ble endret"))

    return render(request, "profiles/index.html", context)


@login_required
def position(request):
    context = _create_profile_context(request)
    context["active_tab"] = "position"

    if request.method == "POST":
        form = PositionForm(request.POST)
        context["position_form"] = form

        if not form.is_valid():
            messages.error(request, _("Skjemaet inneholder feil"))
        else:
            new_position = form.save(commit=False)
            new_position.user = request.user
            new_position.save()
            messages.success(request, _("Posisjonen ble lagret"))

    return render(request, "profiles/index.html", context)


@login_required
def delete_position(request):
    if request.is_ajax():
        if request.method == "POST":
            position_id = request.POST.get("position_id")
            pos = get_object_or_404(Position, pk=position_id)
            if pos.user == request.user:
                pos.delete()
                return_status = json.dumps({"message": _("Posisjonen ble slettet.")})
                return HttpResponse(status=200, content=return_status)
            else:
                return_status = json.dumps(
                    {
                        "message": _(
                            "Du prøvde å slette en posisjon som ikke tilhørte deg selv."
                        )
                    }
                )
            return HttpResponse(status=500, content=return_status)
        raise Http404


@login_required
def update_mark_rules(request):
    if request.is_ajax():
        if request.method == "POST":
            accepted = request.POST.get("rules_accepted") == "true"
            if accepted:
                return_status = json.dumps(
                    {"message": _("Du har valgt å akseptere prikkereglene.")}
                )
                MarkRuleSet.accept_mark_rules(request.user)
            else:
                return_status = json.dumps(
                    {
                        "message": _(
                            "Du kan ikke endre din godkjenning av prikkereglene."
                        )
                    }
                )
                return HttpResponse(status=403, content=return_status)
            return HttpResponse(status=212, content=return_status)
    return HttpResponse(status=405)


@login_required
def toggle_infomail(request):
    """
    Toggles the infomail field in Onlineuser object
    """
    if request.is_ajax():
        if request.method == "POST":
            request.user.infomail = not request.user.infomail
            request.user.save()

            return HttpResponse(
                status=200, content=json.dumps({"state": request.user.infomail})
            )
    raise Http404


@login_required
def toggle_jobmail(request):
    """
    Toggles the jobmail field in Onlineuser object
    """
    if request.is_ajax():
        if request.method == "POST":
            request.user.jobmail = not request.user.jobmail
            request.user.save()

            return HttpResponse(
                status=200, content=json.dumps({"state": request.user.jobmail})
            )
    raise Http404


@login_required
def user_search(request):
    committee_groups = OnlineGroup.objects.filter(
        Q(group_type=GroupType.COMMITTEE) | Q(group_type=GroupType.NODE_COMMITTEE)
    )
    groups_to_include = [online_group.group.pk for online_group in committee_groups]
    groups = Group.objects.filter(pk__in=groups_to_include).order_by("name")
    users_to_display = User.objects.filter(privacy__visible_for_other_users=True)

    context = {"users": users_to_display, "groups": groups}
    return render(request, "profiles/users.html", context)


@login_required
def api_user_search(request):
    if request.GET.get("query"):
        users = search_for_users(request.GET.get("query"))
        return render_json(users)
    return render_json(error="Mangler søkestreng")


def search_for_users(query, limit=10):
    if not query:
        return []

    results = []

    for result in watson.search(
        query, models=(User.objects.filter(privacy__visible_for_other_users=True),)
    ):
        results.append(result.object)

    return results[:limit]


@login_required
def api_plain_user_search(request):
    """The difference between plain_user_search and the other is exposing only id and name."""
    if request.GET.get("query"):
        users = search_for_plain_users(request.GET.get("query"))
        return JsonResponse(users, safe=False)
    return render_json(error="Mangler søkestreng")


def search_for_plain_users(query, limit=10):
    if not query:
        return []

    results = []

    for result in watson.search(query, models=(User.objects.filter(is_active=True),)):
        uobj = result.object
        results.append({"id": uobj.id, "value": uobj.get_full_name()})

    return results[:limit]


@login_required
def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    if user.privacy.visible_for_other_users or user == request.user:
        return render(request, "profiles/view_profile.html", {"user_profile": user})

    messages.error(request, _("Du har ikke tilgang til denne profilen"))
    return redirect("profiles")


@login_required
def feedback_pending(request):
    return render(request, "profiles/feedback_pending.html", {})


class GSuiteCreateAccount(View):
    def post(self, request, *args, **kwargs):
        try:
            create_g_suite_account(request.user)
            messages.success(
                request,
                "Opprettet en G Suite konto til deg. Sjekk primærepostadressen din ({}) for instruksjoner.".format(
                    request.user.primary_email
                ),
            )
        except HttpError as err:
            if err.resp.status == 409:
                messages.error(
                    request,
                    "Det finnes allerede en brukerkonto med dette brukernavnet i G Suite. "
                    "Dersom du mener det er galt, ta kontakt med dotkom.",
                )
            else:
                messages.error(
                    request, "Noe gikk galt. Vennligst ta kontakt med dotkom."
                )

        return redirect("profile_add_email")


class GSuiteResetPassword(View):
    def post(self, request, *args, **kwargs):
        try:
            reset_password_g_suite_account(request.user)
            messages.success(
                request,
                "Du har fått satt et nytt passord. Sjekk primæreposten din for informasjon.",
            )
        except ValueError as err:
            messages.error(request, err)

        return redirect("profile_add_email")


class PublicProfileSearchSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    queryset = User.objects.filter(privacy__visible_for_other_users=True)
    serializer_class = PublicProfileSerializer
    search_fields = ("username", "first_name", "last_name")
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = PublicProfileFilter
    permission_classes = (permissions.IsAuthenticated,)


class PersonalPrivacyView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, format=None):
        privacy = Privacy.objects.get(user=request.user)
        serializer = PrivacySerializer(privacy)
        return response.Response(serializer.data)

    def put(self, request, pk=None):
        privacy = Privacy.objects.get(user=request.user)
        serializer = PrivacySerializer(privacy, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return response.Response(serializer.data)


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, format=None):
        user = request.user
        serializer = ProfileSerializer(user)
        return response.Response(serializer.data)

    def put(self, request, pk=None):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user)
            return response.Response(serializer.data)


class UserEmailAddressesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """TODO: Support creation of mail, and updating of primary mail"""

    serializer_class = EmailReadOnlySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Email.objects.filter(user=self.request.user)
