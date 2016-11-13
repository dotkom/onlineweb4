from django.conf import settings


def context_settings(request):
    context_extras = {}
    if hasattr(settings, 'GOOGLE_ANALYTICS_KEY'):
        context_extras['GOOGLE_ANALYTICS_KEY'] = settings.GOOGLE_ANALYTICS_KEY
    if hasattr(settings, 'HOT_RELOAD'):
        context_extras['HOT_RELOAD'] = settings.HOT_RELOAD
    return context_extras
