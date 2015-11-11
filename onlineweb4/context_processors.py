from django.conf import settings


def analytics(request):
	context_extras = {}
	if hasattr(settings, 'GOOGLE_ANALYTICS_KEY'):
		context_extras['GOOGLE_ANALYTICS_KEY'] = settings.GOOGLE_ANALYTICS_KEY
	return context_extras
