# -*- encoding: utf-8 -*-
from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def in_group(context, group):
    return context['request'].user.in_group(group)
