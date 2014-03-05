# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.inclusion_tag('pizza/admin_tabs.html')
def admin_tabs(active):
    return {'active': active}
