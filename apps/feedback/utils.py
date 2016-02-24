# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType

from apps.events.models import Event
from apps.events.utils import get_group_restricted_events
from apps.feedback.models import FeedbackRelation


def has_permission(feedback_relation, user):
    content_object = feedback_relation.content_object

    if isinstance(content_object, Event):
        return content_object in get_group_restricted_events(user)

    # If the object is not an event return false by default
    return False


def can_delete(text_answer, user):
    feedback_relation = text_answer.feedback_relation

    return has_permission(feedback_relation, user)


def get_group_restricted_feedback_relations(user):
    events = get_group_restricted_events(user, True)

    return FeedbackRelation.objects.filter(object_id__in=events, content_type=ContentType.objects.get(model="event"))
