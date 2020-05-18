from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from apps.authentication.models import OnlineGroup
from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_group, send_message_to_users

from .models import CommitteeApplication


def send_approval_notification(approval):
    d = {"approval": approval, "approval_url": settings.BASE_URL + reverse("approvals")}

    approval_group = OnlineGroup.objects.get(name_long="Hovedstyret")  # TODO: Don't
    content = render_to_string("approval/email/approval_notification.txt", d)

    send_message_to_group(
        title=f"[Medlemskapssøknad] {approval.applicant.get_full_name()}",
        content=content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        group=approval_group,
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


def send_committee_application_notification_to_admins(application):
    context = {
        "link_to_admin": True,
        "absolute_url": settings.BASE_URL + application.get_absolute_url(),
        "applicant_name": application.get_name(),
    }
    message = render_to_string(
        "approval/email/committeeapplication_notification.txt", context
    )
    approval_group = OnlineGroup.objects.get(name_long="Hovedstyret")  # TODO: Don't
    send_message_to_group(
        title="[opptak] Bekreftelse på komitesøknad",
        content=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        group=approval_group,
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
    title = "[opptak] Bekreftelse på komitesøknad"
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
