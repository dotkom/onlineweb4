from django.conf import settings

from apps.feedback.models import FeedbackRelation

def context_settings(request):
    context_extras = {}
    if hasattr(settings, 'GOOGLE_ANALYTICS_KEY'):
        context_extras['GOOGLE_ANALYTICS_KEY'] = settings.GOOGLE_ANALYTICS_KEY
    if hasattr(settings, 'HOT_RELOAD'):
        context_extras['HOT_RELOAD'] = settings.HOT_RELOAD
    return context_extras

def feedback_notifier(request):
    context_extras = {}
    context_extras['feedback_pending'] = []
    if not request.user.is_authenticated():
        return context_extras

    active_feedbacks = FeedbackRelation.objects.filter(active=True)
    for active_feedback in active_feedbacks:
        if active_feedback.content_object is None:
            continue

        # This method returns both bools and a list for some reason. Python crashes with the expression: x in bool,
        # so we do this to fetch once and test twice
        not_answered = active_feedback.not_answered()
        if not_answered == False or request.user not in not_answered:
            continue

        context_extras['feedback_pending'].append(active_feedback)

    return context_extras
