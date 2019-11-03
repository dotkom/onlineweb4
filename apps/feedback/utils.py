# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import get_objects_for_user

from apps.authentication.models import OnlineUser as User
from apps.events.models import Event
from apps.feedback.models import FeedbackRelation


def has_permission(feedback_relation, user: User):
    content_object = feedback_relation.content_object

    if isinstance(content_object, Event):
        event: Event = content_object
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.has_perm("events.change_event", event)

    # If the object is not an event return false by default
    return False


def can_delete(text_answer, user):
    feedback_relation = text_answer.feedback_relation

    return has_permission(feedback_relation, user)


def get_group_restricted_feedback_relations(user: User):
    if not user.is_authenticated:
        events = Event.objects.none()
    elif user.is_superuser:
        events = Event.objects.all()
    else:
        events = get_objects_for_user(
            user, "events.change_event", accept_global_perms=False
        )

    return FeedbackRelation.objects.filter(
        object_id__in=events, content_type=ContentType.objects.get(model="event")
    )
