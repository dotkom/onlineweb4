
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from guardian.models import GroupObjectPermission, UserObjectPermission

from apps.companyprofile.models import Company


def _handle_poster_add(request, form, order_type):
    logger = logging.getLogger(__name__)

    poster = form.save(commit=False)
    if request.POST.get('company'):
        poster.company = Company.objects.get(pk=request.POST.get('company'))
    poster.ordered_by = request.user
    poster.order_type = order_type

    poster.save()

    # Let this user have permissions to show this order
    UserObjectPermission.objects.assign_perm('view_poster_order', request.user, poster)
    GroupObjectPermission.objects.assign_perm(
        'view_poster_order',
        Group.objects.get(name='proKom'),
        poster
    )

    title = str(poster)

    # The great sending of emails
    subject = '[ProKom] Ny bestilling | %s' % title

    poster.absolute_url = request.build_absolute_uri(poster.get_dashboard_url())
    context = {}
    context['poster'] = poster
    message = render_to_string('posters/email/new_order_notification.txt', context)

    from_email = settings.EMAIL_PROKOM
    to_emails = [settings.EMAIL_PROKOM, request.user.get_email().email]

    try:
        email_sent = EmailMessage(subject, message, from_email, to_emails, []).send()
    except ImproperlyConfigured:
        email_sent = False
        logger.warn("Failed to send email for new order")
    if email_sent:
        messages.success(request, 'Opprettet bestilling')
    else:
        messages.error(request, 'Klarte ikke å sende epost, men bestillingen din ble fortsatt opprettet')

    if(poster.id % 100 == 0):
        _handle_poster_celebration(poster, context)


def _handle_poster_celebration(poster, context):
        logger = logging.getLogger(__name__)
        subject = '[DotKom] {} Postere!'.format(poster.id)
        message = render_to_string('posters/email/100_multiple_order.txt', context)

        from_email = settings.EMAIL_DOTKOM
        to_email = [settings.EMAIL_PROKOM]
        try:
            EmailMessage(subject, message, from_email, to_email, []).send()
        except ImproperlyConfigured:
            logger.warn("Failed to send email Congratulating ProKom with number of poster orders divisible by 100")
