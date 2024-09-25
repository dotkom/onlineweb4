from django.conf import settings
from django.utils import timezone

from apps.feedback.models import FeedbackRelation


def context_settings(request):
    context_extras = {}
    if hasattr(settings, "ENVIRONMENT"):
        context_extras["ENVIRONMENT"] = settings.ENVIRONMENT
    return context_extras


def feedback_notifier(request):
    context_extras = {}
    context_extras["feedback_pending"] = []
    if not request.user.is_authenticated:
        return context_extras

    active_feedbacks = (
        FeedbackRelation.objects.select_related("content_type")
        .prefetch_related("content_object")
        .filter(active=True)
    )
    for active_feedback in active_feedbacks:
        if active_feedback.content_object is None:
            continue

        # Making sure we have an end data, and that the event is over
        # and that the feedback deadline is not passed (logic reused from apps.feedback.mommy)
        end_date = active_feedback.content_end_date()
        today_date = timezone.now().date()
        if (
            not end_date
            or end_date.date() >= today_date
            or (active_feedback.deadline - today_date).days < 0
        ):
            continue

        # This method returns both bools and a list for some reason. Python crashes with the expression: x in bool,
        # so we do this to fetch once and test twice
        not_answered = active_feedback.not_answered()
        if request.user not in not_answered:
            continue

        context_extras["feedback_pending"].append(active_feedback)

    return context_extras
