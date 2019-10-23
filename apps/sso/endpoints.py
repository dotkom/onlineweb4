# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/27/15

from django.http import JsonResponse
from oauth2_provider.decorators import protected_resource

from apps.sso.userinfo import Onlineweb4Userinfo

USERINFO_SCOPES = [
    "authentication.onlineuser.username.read",
    "authentication.onlineuser.first_name.read",
    "authentication.onlineuser.last_name.read",
    "authentication.onlineuser.email.read",
    "authentication.onlineuser.is_member.read",
    "authentication.onlineuser.is_staff.read",
    "authentication.onlineuser.is_superuser.read",
    "authentication.onlineuser.field_of_study.read",
    "authentication.onlineuser.nickname.read",
    "authentication.onlineuser.rfid.read",
]


@protected_resource(USERINFO_SCOPES)
def oauth2_provider_userinfo(request):
    """
    Basic user information provided based on the Bearer Token provided by an SSO application
    :param request: The Django Request object
    :return: An HTTP response
    """
    return JsonResponse(status=200, data=Onlineweb4Userinfo(request.user).oauth2())
