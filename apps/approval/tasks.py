import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse

from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_users

from .models import Approval


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
            f"Failed to send approval approver notification email for approval#{approval.pk}."
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
