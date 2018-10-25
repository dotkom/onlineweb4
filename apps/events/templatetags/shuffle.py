import random
from django import template

register = template.Library()

@register.filter
def shuffle(arg):
    li = list(arg)
    random.shuffle(li)
    return li
