import re

from django import template

register = template.Library()


@register.filter
def unhttps(url):
    return re.sub(r"^https", "http", url)
