import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.db.models import Q
from django.template.loader import render_to_string
from guardian.models import GroupObjectPermission, UserObjectPermission

from apps.authentication.models import OnlineUser as User
from apps.companyprofile.models import Company

from ..models import Poster


def _handle_poster_add(request, form, order_type):
    logger = logging.getLogger(__name__)

    poster = form.save(commit=False)
    if request.POST.get("company"):
        poster.company = Company.objects.get(pk=request.POST.get("company"))
    poster.ordered_by = request.user
    poster.order_type = order_type

    poster.save()
    ordered_committee = form.cleaned_data["ordered_committee"]
    poster_admin_group = get_poster_admin_group()

    # Let this user have permissions to show this order
    UserObjectPermission.objects.assign_perm("view_poster_order", request.user, poster)
    GroupObjectPermission.objects.assign_perm(
        "view_poster_order", poster_admin_group, poster
    )
    GroupObjectPermission.objects.assign_perm(
        "view_poster_order", ordered_committee, poster
    )

    title = str(poster)

    # The great sending of emails
    subject = "[prokom] Ny bestilling | %s" % title

    poster.absolute_url = request.build_absolute_uri(poster.get_dashboard_url())
    context = {}
    context["poster"] = poster
    message = render_to_string("posters/email/new_order_notification.txt", context)

    from_email = settings.EMAIL_PROKOM
    to_emails = [settings.EMAIL_PROKOM, request.user.primary_email]

    try:
        email_sent = EmailMessage(subject, message, from_email, to_emails, []).send()
    except ImproperlyConfigured:
        email_sent = False
        logger.exception("Failed to send email for new order")
    if email_sent:
        messages.success(request, "Opprettet bestilling")
    else:
        messages.error(
            request,
            "Klarte ikke å sende epost, men bestillingen din ble fortsatt opprettet",
        )

    if poster.id % 100 == 0:
        _handle_poster_celebration(poster, context)


def _handle_poster_celebration(poster, context):
    logger = logging.getLogger(__name__)
    subject = "[dotkom] Gratulerer med {} plakater!".format(poster.id)
    message = render_to_string("posters/email/100_multiple_order.txt", context)

    from_email = settings.EMAIL_DOTKOM
    to_email = [settings.EMAIL_PROKOM]
    try:
        EmailMessage(subject, message, from_email, to_email, []).send()
    except ImproperlyConfigured:
        logger.exception(
            "Failed to send email Congratulating ProKom with number of poster orders divisible by 100"
        )


def get_poster_admins():
    """
    Return a queryset of all users with the global permission to change posters.
    """
    content_type = ContentType.objects.get_for_model(Poster)
    all_permissions = Permission.objects.filter(content_type=content_type)
    change_order_perm = all_permissions.filter(codename="change_poster").first()
    users = User.objects.filter(
        Q(groups__permissions=change_order_perm) | Q(user_permissions=change_order_perm)
    ).distinct()
    return users

def get_poster_admin_group():
    content_type = ContentType.objects.get_for_model(Poster)
    all_permissions = Permission.objects.filter(content_type=content_type)
    change_order_perm = all_permissions.filter(codename="change_poster").first()
    admin_group = Group.objects.filter(permissions=change_order_perm).distinct()
    return admin_group

