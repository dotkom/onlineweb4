import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


def send_approval_notification(approval):
    logger = logging.getLogger(__name__)
    d = {
        'approval': approval,
        'approval_url': settings.BASE_URL + reverse('approvals')
    }

    to_emails = [settings.EMAIL_HS]
    content = render_to_string('approval/email/approval_notification.txt', d)

    try:
        EmailMessage("[Medlemskapssøknad] %s" % approval.applicant.get_full_name(),
                     content, settings.DEFAULT_FROM_EMAIL, to_emails).send()
    except ImproperlyConfigured:
        logger.warn('Failed to send approval approver notification email for approval#{pk}.'.format(
            {'pk': approval.pk}))

def send_approval_status_update(approval):
    logger = logging.getLogger(__name__)

    accepted = approval.approved
    message = "Ditt medlemskap i Online er "
    if accepted:
        message += "godkjent."
    else:
        message += "ikke godkjent."
        if len(approval.message) == 0:
            message += " Ta kontakt med Online for begrunnelse."
        else: message += approval.message
    try:
        EmailMessage("Soknad om medlemskap i Online er vurdert",
                     message,
                     settings.DEFAULT_FROM_EMAIL,
                     [approval.applicant.get_email()],
                     ).send()
    except ImproperlyConfigured:
        logger.warn('Failed to notify applicant about updated status on membership for approval#{pk}.'.format(
            {'pk': approval.pk}))
