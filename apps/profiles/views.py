# -*- coding: utf-8 -*-
import json
import logging
import re
import uuid
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views import View
from googleapiclient.errors import HttpError
from oauth2_provider.models import AccessToken
from watson import search as watson

from apps.approval.forms import FieldOfStudyApplicationForm
from apps.approval.models import MembershipApproval
from apps.authentication.forms import NewEmailForm
from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, RegisterToken
from apps.authentication.utils import create_online_mail_alias
from apps.dashboard.tools import has_access
from apps.gsuite.accounts.main import create_g_suite_account, reset_password_g_suite_account
from apps.marks.models import Mark, Suspension
from apps.payment.models import PaymentDelay, PaymentRelation, PaymentTransaction
from apps.profiles.forms import InternalServicesForm, PositionForm, PrivacyForm, ProfileForm
from apps.profiles.models import Privacy
from apps.shop.models import Order
from utils.shortcuts import render_json


"""
Index for the entire user profile view
Methods redirect to this view on save
"""


@login_required
def index(request, active_tab='overview'):
    context = _create_profile_context(request)
    context['active_tab'] = active_tab

    return render(request, 'profiles/index.html', context)


def _create_profile_context(request):
    groups = Group.objects.all()

    Privacy.objects.get_or_create(user=request.user)  # This is a hack
    """
    To make sure a privacy exists when visiting /profiles/privacy/.
    Until now, it has been generated upon loading models.py, which is a bit hacky.
    The code is refactored to use Django signals, so whenever a user is created, a privacy-property is set up.
    """

    if request.user.is_staff and not request.user.online_mail:
        create_online_mail_alias(request.user)

    context = {
        # edit
        'position_form': PositionForm(),
        'user_profile_form': ProfileForm(instance=request.user),
        # positions
        'groups': groups,
        # privacy
        'privacy_form': PrivacyForm(instance=request.user.privacy),
        # nibble information
        'transactions': PaymentTransaction.objects.filter(user=request.user),
        'orders': Order.objects.filter(order_line__user=request.user).order_by('-order_line__datetime'),

        # SSO / OAuth2 approved apps
        'connected_apps': AccessToken.objects.filter(user=request.user, expires__gte=timezone.now()).order_by(
            'expires'),

        # marks
        'mark_rules_accepted': request.user.mark_rules,
        'marks': [
            # Tuple syntax ('title', list_of_marks, is_collapsed)
            (_('aktive prikker'), Mark.marks.active(request.user), False),
            (_('inaktive prikker'), Mark.marks.inactive(request.user), True),
        ],
        'suspensions': [
            # Tuple syntax ('title', list_of_marks, is_collapsed)
            (_('aktive suspensjoner'), Suspension.objects.filter(user=request.user, active=True), False),
            (_('inaktive suspensjoner'), Suspension.objects.filter(user=request.user, active=False), True),
        ],
        # password
        'password_change_form': PasswordChangeForm(request.user),
        # email
        'new_email': NewEmailForm(),
        # approvals
        'field_of_study_application': FieldOfStudyApplicationForm(),
        'has_active_approvals': MembershipApproval.objects.filter(applicant=request.user, processed=False).count() > 0,
        'approvals': [
            # Tuple syntax ('title', list_of_approvals, is_collapsed)
            (_("aktive søknader"), MembershipApproval.objects.filter(applicant=request.user, processed=False), False),
            (_("avslåtte søknader"), MembershipApproval.objects.filter(
                applicant=request.user,
                processed=True,
                approved=False
            ), True),
            (_("godkjente søknader"), MembershipApproval.objects.filter(applicant=request.user, processed=True), True),
        ],
        'payments': [
            (_('ubetalt'), PaymentDelay.objects.all().filter(user=request.user, active=True), False),
            (_('betalt'), PaymentRelation.objects.all().filter(user=request.user), True),
        ],
        'internal_services_form': InternalServicesForm(),
        'in_comittee': has_access(request),
        'enable_dataporten_application':
            settings.DATAPORTEN.get('STUDY').get('ENABLED') or settings.DATAPORTEN.get('STUDY').get('TESTING'),
    }

    return context


@login_required
def edit_profile(request):
    context = _create_profile_context(request)
    context['active_tab'] = 'edit'

    if request.method == 'POST':
        user_profile_form = ProfileForm(request.POST, instance=request.user)
        context['user_profile_form'] = user_profile_form

        if not user_profile_form.is_valid():
            messages.error(request, _("Noen av de påkrevde feltene mangler"))
        else:
            user_profile_form.save()
            messages.success(request, _("Brukerprofilen din ble endret"))

    return render(request, 'profiles/index.html', context)


@login_required
def privacy(request):
    context = _create_profile_context(request)
    context['active_tab'] = 'privacy'

    if request.method == 'POST':
        privacy_form = PrivacyForm(request.POST, instance=request.user.privacy)
        context['privacy_form'] = privacy_form

        if not privacy_form.is_valid():
            messages.error(request, _("Noen av de påkrevde feltene mangler"))
        else:
            privacy_form.save()
            messages.success(request, _("Personvern ble endret"))

    return render(request, 'profiles/index.html', context)


@login_required()
def connected_apps(request):
    """
    Tab controller for the connected 3rd party apps pane
    :param request: Django request object
    :return: An HttpResponse
    """

    context = _create_profile_context(request)
    context['active_tab'] = 'connected_apps'

    if request.method == 'POST':
        if 'token_id' not in request.POST:
            messages.error(request, _('Det ble ikke oppgitt noen tilgangsnøkkel i forespørselen.'))
        else:
            try:
                pk = int(request.POST['token_id'])
                token = get_object_or_404(AccessToken, pk=pk)
                token.delete()
                messages.success(request, _('Tilgangsnøkkelen ble slettet.'))
            except ValueError:
                messages.error(request, _('Tilgangsnøkkelen inneholdt en ugyldig verdi.'))

    return render(request, 'profiles/index.html', context)


@login_required
def password(request):
    context = _create_profile_context(request)
    context['active_tab'] = 'password'

    if request.method == 'POST':
        password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        context['password_change_form'] = password_change_form

        if not password_change_form.is_valid():
            messages.error(request, _("Passordet ditt ble ikke endret"))
        else:
            password_change_form.save()
            messages.success(request, _("Passordet ditt ble endret"))

    return render(request, 'profiles/index.html', context)


@login_required
def position(request):
    context = _create_profile_context(request)
    context['active_tab'] = 'position'

    if request.method == 'POST':
        form = PositionForm(request.POST)
        context['position_form'] = form

        if not form.is_valid():
            messages.error(request, _('Skjemaet inneholder feil'))
        else:
            new_position = form.save(commit=False)
            new_position.user = request.user
            new_position.save()
            messages.success(request, _('Posisjonen ble lagret'))

    return render(request, 'profiles/index.html', context)


@login_required
def delete_position(request):
    if request.is_ajax():
        if request.method == 'POST':
            position_id = request.POST.get('position_id')
            pos = get_object_or_404(Position, pk=position_id)
            if pos.user == request.user:
                pos.delete()
                return_status = json.dumps({'message': _("Posisjonen ble slettet.")})
                return HttpResponse(status=200, content=return_status)
            else:
                return_status = json.dumps({
                    'message': _("Du prøvde å slette en posisjon som ikke tilhørte deg selv.")
                })
            return HttpResponse(status=500, content=return_status)
        raise Http404


@login_required
def update_mark_rules(request):
    if request.is_ajax():
        if request.method == 'POST':
            accepted = request.POST.get('rules_accepted') == "true"
            if accepted:
                return_status = json.dumps({'message': _("Du har valgt å akseptere prikkereglene.")})
                request.user.mark_rules = True
                request.user.save()
            else:
                return_status = json.dumps({'message': _("Du kan ikke endre din godkjenning av prikkereglene.")})
                return HttpResponse(status=403, content=return_status)
            return HttpResponse(status=212, content=return_status)
    return HttpResponse(status=405)


@login_required
def add_email(request):
    context = _create_profile_context(request)
    context['active_tab'] = 'email'

    if request.method == 'POST':
        form = NewEmailForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            email_string = cleaned['new_email'].lower()

            # Check if the email already exists
            if Email.objects.filter(email=cleaned['new_email']).count() > 0:
                messages.error(request, _("Eposten %s er allerede registrert.") % email_string)
                return redirect('profiles')

            # Check if it's studmail and if someone else already has it in their profile
            if re.match(r'[^@]+@stud\.ntnu\.no', email_string):
                ntnu_username = email_string.split("@")[0]
                user = User.objects.filter(ntnu_username=ntnu_username)
                if user.count() == 1:
                    if user[0] != request.user:
                        messages.error(request, _("En bruker med dette NTNU-brukernavnet eksisterer allerede."))
                        return redirect('profiles')

            # Create the email
            email = Email(email=email_string, user=request.user)
            email.save()

            # Send the verification mail
            _send_verification_mail(request, email.email)

            messages.success(request, _("Eposten ble lagret. Du må sjekke din innboks for å verifisere den."))

    return render(request, 'profiles/index.html', context)


@login_required
def delete_email(request):
    if request.is_ajax():
        if request.method == 'POST':
            email_string = request.POST.get('email')
            email = get_object_or_404(Email, email=email_string)

            # Check if the email belongs to the registered user
            if email.user != request.user:
                return HttpResponse(
                    status=412,
                    content=json.dumps({
                        'message': _("%s er ikke en eksisterende epostaddresse på din profil.") % email.email
                    })
                )

            # Users cannot delete their primary email, to avoid them deleting all their emails
            if email.primary:
                return HttpResponse(
                    status=412,
                    content=json.dumps({
                        'message': _("Kan ikke slette primær-epostadresse.")
                    })
                )

            email.delete()
            return HttpResponse(status=200)
    return HttpResponse(status=404)


@login_required
def set_primary(request):
    if request.is_ajax():
        if request.method == 'POST':
            email_string = request.POST.get('email')
            email = get_object_or_404(Email, email=email_string)

            # Check if the email belongs to the registered user
            if email.user != request.user:
                return HttpResponse(
                    status=412,
                    content=json.dumps({
                        'message': _("%s er ikke en eksisterende epostaddresse på din profil.") % email.email}
                    )
                )

            # Check if it was already primary
            if email.primary:
                return HttpResponse(
                    status=412,
                    content=json.dumps({
                        'message': _("%s er allerede satt som primær-epostaddresse.") % email.email}
                    )
                )

            # Deactivate the old primary, if there was one
            primary_email = request.user.get_email()
            if primary_email:
                primary_email.primary = False
                primary_email.save()
            # Activate new primary
            email.primary = True
            email.save()

            return HttpResponse(status=200)
    raise Http404


@login_required
def verify_email(request):
    if request.is_ajax():
        if request.method == 'POST':
            email_string = request.POST.get('email')
            email = get_object_or_404(Email, email=email_string)

            # Check if the email belongs to the registered user
            if email.user != request.user:
                return HttpResponse(
                    status=412,
                    content=json.dumps({
                        'message': _("%s er ikke en eksisterende epostaddresse på din profil.") % email.email}
                    )
                )

            # Check if it was already verified
            if email.verified:
                return HttpResponse(
                    status=412,
                    content=json.dumps({
                        'message': _("%s er allerede verifisert.") % email.email}
                    )
                )

            # Send the verification mail
            _send_verification_mail(request, email.email)

            return HttpResponse(status=200)
    raise Http404


def _send_verification_mail(request, email):
    log = logging.getLogger(__name__)
    # Create the registration token
    token = uuid.uuid4().hex
    try:
        rt = RegisterToken(user=request.user, email=email, token=token)
        rt.save()
        log.info('Successfully registered token for %s' % request.user)
    except IntegrityError as ie:
        log.error('Failed to register token for %s due to %s' % (request.user, ie))
        raise ie

    email_message = _("""
En ny epost har blitt registrert på din profil på online.ntnu.no.

For å kunne ta eposten i bruk kreves det at du verifiserer den. Du kan gjore dette
ved å besøke lenken under.

http://%s/auth/verify/%s/

Denne lenken vil være gyldig i 24 timer. Dersom du behøver å få tilsendt en ny lenke
kan dette gjøres ved å klikke på knappen for verifisering på din profil.
""") % (request.META['HTTP_HOST'], token)

    try:
        send_mail(_('Verifiser din epost %s') % email, email_message, settings.DEFAULT_FROM_EMAIL, [email])
    except SMTPException:
        messages.error(request, 'Det oppstod en kritisk feil, epostadressen er ugyldig!')
        return redirect('home')


@login_required
def toggle_infomail(request):
    """
    Toggles the infomail field in Onlineuser object
    """
    if request.is_ajax():
        if request.method == 'POST':
            request.user.infomail = not request.user.infomail
            request.user.save()

            return HttpResponse(status=200, content=json.dumps({'state': request.user.infomail}))
    raise Http404


@login_required
def toggle_jobmail(request):
    """
    Toggles the jobmail field in Onlineuser object
    """
    if request.is_ajax():
        if request.method == 'POST':
            request.user.jobmail = not request.user.jobmail
            request.user.save()

            return HttpResponse(status=200, content=json.dumps({'state': request.user.jobmail}))
    raise Http404


@login_required
def user_search(request):
    groups_to_include = settings.USER_SEARCH_GROUPS
    groups = Group.objects.filter(pk__in=groups_to_include).order_by('name')
    users_to_display = User.objects.filter(privacy__visible_for_other_users=True)

    context = {
        'users': users_to_display,
        'groups': groups,
    }
    return render(request, 'profiles/users.html', context)


@login_required
def api_user_search(request):
    if request.GET.get('query'):
        users = search_for_users(request.GET.get('query'))
        return render_json(users)
    return render_json(error='Mangler søkestreng')


def search_for_users(query, limit=10):
    if not query:
        return []

    results = []

    for result in watson.search(query, models=(User.objects.filter(privacy__visible_for_other_users=True),)):
        results.append(result.object)

    return results[:limit]


@login_required
def api_plain_user_search(request):
    """ The difference between plain_user_search and the other is exposing only id and name. """
    if request.GET.get('query'):
        users = search_for_plain_users(request.GET.get('query'))
        return JsonResponse(users, safe=False)
    return render_json(error='Mangler søkestreng')


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
        return render(request, 'profiles/view_profile.html', {'user_profile': user})

    messages.error(request, _('Du har ikke tilgang til denne profilen'))
    return redirect('profiles')


@login_required
def feedback_pending(request):
    return render(request, 'profiles/feedback_pending.html', {})


class GSuiteCreateAccount(View):
    def post(self, request, *args, **kwargs):

        try:
            create_g_suite_account(request.user)
            messages.success(request,
                             "Opprettet en G Suite konto til deg. Sjekk primærepostadressen din ({}) for instruksjoner."
                             .format(request.user.get_email().email))
        except HttpError as err:
            if err.resp.status == 409:
                messages.error(request, 'Det finnes allerede en brukerkonto med dette brukernavnet i G Suite. '
                               'Dersom du mener det er galt, ta kontakt med dotkom.')
            else:
                messages.error(request, 'Noe gikk galt. Vennligst ta kontakt med dotkom.')

        return redirect('profile_add_email')


class GSuiteResetPassword(View):
    def post(self, request, *args, **kwargs):
        try:
            reset_password_g_suite_account(request.user)
            messages.success(request, "Du har fått satt et nytt passord. Sjekk primæreposten din for informasjon.")
        except ValueError as err:
            messages.error(request, err)

        return redirect('profile_add_email')
