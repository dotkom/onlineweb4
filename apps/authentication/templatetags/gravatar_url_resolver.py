from django import template
from django.conf import settings
import urllib, hashlib
 
register = template.Library()

@register.assignment_tag(takes_context=True)
def gravatar_url(context, user, size):
    default = "%s%s_%s.png" % (context['request'].META['HTTP_HOST'],
                               settings.DEFAULT_PROFILE_PICTURE_PREFIX, user.gender)
    gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(user.get_email().email).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d': default, 's':str(size)})

    return gravatar_url