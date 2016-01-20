from django import template
import re

register = template.Library()


@register.filter
def unhttps(url):
    return re.sub(r'^https', 'http', url)
