import hashlib
import urllib

from django import template
from django.conf import settings

register = template.Library()


@register.assignment_tag(takes_context=True)
def gravatar_url(context, user, size):
    prefix = "https://" if context['request'].is_secure() else "http://"
    default = "%s%s%s_%s.png" % (
        prefix,
        context['request'].META.get('HTTP_HOST', 'localhost'),
        settings.DEFAULT_PROFILE_PICTURE_PREFIX,
        user.gender
    )

    grav_url = "https://www.gravatar.com/avatar/" + hashlib.md5(user.email.encode()).hexdigest() + "?"
    grav_url += urllib.parse.urlencode({'d': default, 's': str(size)})

    return grav_url
