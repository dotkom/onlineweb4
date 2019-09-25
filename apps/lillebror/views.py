import logging

from django.shortcuts import render
from apps.authentication.models import OnlineUser
from django.contrib.auth.models import User


def all_user_data(request):
    logger = logging.getLogger(__name__)
    # user = User.objects.create_user(username='annonymousBird1234',
    #                                 email='annon@ema.il',
    #                                 password='thisisapassword')
    for field in User._meta.get_fields():
        logger.warning(field)
        # user.field.type = get_internal_type()
    return(render(request, "lillebror/index.html"))
