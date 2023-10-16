import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)
from guardian.decorators import permission_required

from apps.authentication.models import Membership
from apps.dashboard.tools import DashboardPermissionMixin, get_base_context, has_access

from ..models import CommitteeApplicationPeriod, MembershipApproval
from .forms import (
    ApplicationPeriodParticipantsUpdateForm,
    CommitteeApplicationPeriodForm,
)


@ensure_csrf_cookie
@login_required
@permission_required("approval.view_membershipapproval", return_403=True)
def index(request):
    # Generic check to see if user has access to dashboard. (Is staff or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context["membership_applications"] = MembershipApproval.objects.filter(
        processed=False
    )
    context["processed_applications"] = MembershipApproval.objects.filter(
        processed=True
    ).order_by("-processed_date")[:10]

    return render(request, "approval/dashboard/index.html", context)


@ensure_csrf_cookie
@login_required
@permission_required("approval.change_membershipapproval", return_403=True)
def approve_application(request):
    if request.is_ajax():
        if request.method == "POST":
            application_id = request.POST.get("application_id")
            apps = MembershipApproval.objects.filter(pk=application_id)

            if apps.count() == 0:
                response_text = json.dumps(
                    {
                        "message": _(
                            """Kan ikke finne en søknad med denne IDen (%s).
Om feilen vedvarer etter en refresh, kontakt dotkom@online.ntnu.no."""
                        )
                        % application_id
                    }
                )
                return HttpResponse(status=412, content=response_text)

            app = apps[0]

            if app.processed:
                response_text = json.dumps(
                    {"message": _("Denne søknaden er allerede behandlet.")}
                )
                return HttpResponse(status=412, content=response_text)

            user = app.applicant

            if not user.ntnu_username:
                response_text = json.dumps(
                    {
                        "message": _(
                            """Brukeren (%s) har ikke noe lagret ntnu brukernavn."""
                        )
                        % user.get_full_name()
                    }
                )
                return HttpResponse(status=412, content=response_text)

            if app.is_fos_application():
                user.field_of_study = app.field_of_study
                user.started_date = app.started_date
                user.save()

            if app.is_membership_application():
                membership = Membership.objects.filter(username=user.ntnu_username)
                if membership.count() == 1:
                    membership = membership[0]
                    membership.expiration_date = app.new_expiry_date
                    if not membership.description:
                        membership.description = ""
                    membership.description += """
-------------------
Updated by approvals app.

Approved by %s on %s.

Old notes:
%s
""" % (
                        request.user.get_full_name(),
                        str(timezone.now().date()),
                        membership.note,
                    )
                    membership.note = (
                        user.get_field_of_study_display() + " " + str(user.started_date)
                    )
                    membership.save()
                else:
                    membership = Membership()
                    membership.username = user.ntnu_username
                    membership.expiration_date = app.new_expiry_date
                    membership.registered = timezone.now().date()
                    membership.note = (
                        user.get_field_of_study_display() + " " + str(user.started_date)
                    )
                    membership.description = """Added by approvals app.

Approved by %s on %s.""" % (
                        request.user.get_full_name(),
                        str(timezone.now().date()),
                    )
                    membership.save()

            app.processed = True
            app.processed_date = timezone.now()
            app.approved = True
            app.approver = request.user
            app.save()

            return HttpResponse(status=200)

    raise Http404


@login_required
@ensure_csrf_cookie
@permission_required("approval.change_membershipapproval", return_403=True)
def decline_application(request):
    if request.is_ajax():
        if request.method == "POST":
            application_id = request.POST.get("application_id")
            apps = MembershipApproval.objects.filter(pk=application_id)

            if apps.count() == 0:
                response_text = json.dumps(
                    {
                        "message": _(
                            """
Kan ikke finne en søknad med denne IDen (%s).
Om feilen vedvarer etter en refresh, kontakt dotkom@online.ntnu.no."""
                        )
                        % application_id
                    }
                )
                return HttpResponse(status=412, content=response_text)

            app = apps[0]

            if app.processed:
                response_text = json.dumps(
                    {"message": _("Denne søknaden er allerede behandlet.")}
                )
                return HttpResponse(status=412, content=response_text)

            message = request.POST.get("message")

            app.processed = True
            app.processed_date = timezone.now()
            app.approved = False
            app.approver = request.user
            app.message = message
            app.save()

            return HttpResponse(status=200)

    raise Http404


class ApplicationPeriodList(DashboardPermissionMixin, TemplateView):
    model = CommitteeApplicationPeriod
    template_name = "approval/dashboard/application_period/index.html"
    permission_required = "approval.view_committeeapplicationperiod"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["application_periods"] = CommitteeApplicationPeriod.objects.all()
        return context


class ApplicationPeriodCreate(DashboardPermissionMixin, CreateView):
    model = CommitteeApplicationPeriod
    template_name = "approval/dashboard/application_period/create.html"
    permission_required = "approval.add_committeeapplicationperiod"
    form_class = CommitteeApplicationPeriodForm

    def get_success_url(self):
        return reverse("application-periods-list")


class ApplicationPeriodDetail(DashboardPermissionMixin, DetailView):
    model = CommitteeApplicationPeriod
    template_name = "approval/dashboard/application_period/detail.html"
    permission_required = "approval.change_committeeapplicationperiod"
    context_object_name = "application_period"


class ApplicationPeriodUpdate(DashboardPermissionMixin, UpdateView):
    model = CommitteeApplicationPeriod
    template_name = "approval/dashboard/application_period/create.html"
    permission_required = "approval.delete_committeeapplicationperiod"
    form_class = CommitteeApplicationPeriodForm
    context_object_name = "application_period"

    def get_success_url(self):
        return reverse("application-periods-detail", kwargs={"pk": self.object.pk})


class ApplicationPeriodDelete(DashboardPermissionMixin, DeleteView):
    model = CommitteeApplicationPeriod
    template_name = "approval/dashboard/application_period/delete.html"
    permission_required = "approval.delete_committeeapplicationperiod"
    context_object_name = "application_period"

    def get_success_url(self):
        return reverse("application-periods-list")


class ApplicationPeriodParticipantionUpdate(DashboardPermissionMixin, UpdateView):
    model = CommitteeApplicationPeriod
    template_name = "approval/dashboard/application_period/create.html"
    permission_required = "approval.delete_committeeapplicationperiod"
    form_class = ApplicationPeriodParticipantsUpdateForm
    context_object_name = "application_period"

    def post(self, request, *args, **kwargs):
        instance = CommitteeApplicationPeriod.objects.get(pk=kwargs["pk"])
        form = ApplicationPeriodParticipantsUpdateForm(request.POST, instance=instance)
        if form.is_valid():
            committes_to_be_set_true = form.cleaned_data["committees_with_applications"]
            for c in instance.committeeapplicationperiodparticipation_set.all():
                previous_open = c.open_for_applications
                c.open_for_applications = False
                if str(c.pk) in committes_to_be_set_true:
                    c.open_for_applications = True
                if not previous_open == c.open_for_applications:
                    c.save()
            return HttpResponseRedirect(
                reverse("application-periods-detail", kwargs={"pk": instance.pk})
            )
        return super().form_invalid(form)
