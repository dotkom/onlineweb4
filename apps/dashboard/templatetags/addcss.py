# -*- coding: utf-8 -*-

from django import template
register = template.Library()


@register.filter(name='addclass')
def addclass(field, css):

    attrs = {
        u"class": css
    }

    return field.as_widget(attrs=attrs)
