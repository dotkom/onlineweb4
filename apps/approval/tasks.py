import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_users

from .models import Approval, CommitteeApplication


def send_approval_notification(approval: Approval):
    logger = logging.getLogger(__name__)
    d = {"approval": approval, "approval_url": settings.BASE_URL + reverse("approvals")}

    to_emails = [settings.EMAIL_HS]
    content = render_to_string("approval/email/approval_notification.txt", d)

    try:
        EmailMessage(
            "[Medlemskapssøknad] %s" % approval.applicant.get_full_name(),
            content,
            settings.DEFAULT_FROM_EMAIL,
            to_emails,
        ).send()
    except ImproperlyConfigured:
        logger.warning(
            "Failed to send approval approver notification email for approval#{pk}.".format(
                {"pk": approval.pk}
            )
        )


def send_approval_status_update(approval):
    accepted = approval.approved
    message = "Ditt medlemskap i Online er "
    if accepted:
        message += "godkjent."
    else:
        message += "ikke godkjent."
        if len(approval.message) == 0:
            message += " Ta kontakt med Online for begrunnelse."
        else:
            message += approval.message

    send_message_to_users(
        title="Søknad om medlemskap i Online er vurdert",
        content=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipients=[approval.applicant],
        permission_type=PermissionType.APPLICATIONS,
    )


def send_committee_application_notification_to_admins(
    application: CommitteeApplication,
):
    context = {
        "link_to_admin": True,
        "absolute_url": settings.BASE_URL + application.get_absolute_url(),
        "applicant_name": application.get_name(),
    }
    message = render_to_string(
        "approval/email/committeeapplication_notification.txt", context
    )
    send_mail(
        subject="[opptak] Bekreftelse på komitésøknad",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HS],
    )


def send_committee_application_notification_to_applicant(
    application: CommitteeApplication,
):
    context = {
        "link_to_admin": False,
        "absolute_url": settings.BASE_URL + application.get_absolute_url(),
        "applicant_name": application.get_name(),
    }
    message = render_to_string(
        "approval/email/committeeapplication_notification.txt", context
    )
    title = "[opptak] Bekreftelse på komitésøknad"
    if application.applicant:
        send_message_to_users(
            title=title,
            content=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipients=[application.applicant],
            permission_type=PermissionType.APPLICATIONS,
        )
    else:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.email],
        )
