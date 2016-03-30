from collections import defaultdict
from importlib import import_module

from django import template

from apps.feedback.models import FIELD_OF_STUDY_CHOICES, RATING_CHOICES

register = template.Library()


@register.filter
def isinst(value, class_str):
    """
    isinstance in django templates.
    """
    split = class_str.split('.')
    return isinstance(value, getattr(import_module('.'.join(split[:-1])), split[-1]))


@register.filter
def count_fos(value):
    """
    Count field of study answers
    """
    answer_count = defaultdict(int)
    for answer in value:
        answer_count[str(answer)] += 1

    ordered_answers = []
    for _, x in FIELD_OF_STUDY_CHOICES[1:]:
        ordered_answers.append([x, answer_count[x]])
    return ordered_answers


@register.filter
def count_rating(value):
    """
    Count rating answers
    """
    answer_count = defaultdict(int)
    for answer in value:
        answer_count[str(answer)] += 1

    ordered_answers = []
    for _, x in RATING_CHOICES:
        ordered_answers.append([x, answer_count[x]])
    return ordered_answers
