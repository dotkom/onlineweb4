import logging

from django.conf import settings
from django.core.mail import EmailMessage, send_mail


def send_report_on_photo(user, photo, description):
	logger = logging.getLogger(__name__)

	to_email = [settings.EMAIL_PROKOM]
	content = "Bruker %s har rapportert bilde %s med begrunnelse %s" % user.name, photo, description

	try:
		email = EmailMessage("[Rapportering av bilde]", content, settings.DEFAULT_FROM_EMAIL, to_emails)#.send())
		print(email)
	except ImproperlyConfigured:
		logger.warn('Failed to send the report of the photo to prokom from user {user} on photo #{pk}.'.format(
            {'user': user.name, 'pk': photo.pk}))
