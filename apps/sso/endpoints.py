# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/27/15

from django.http import JsonResponse
from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import AccessToken

SCOPES = [
    'authentication.onlineuser.username.read',
    'authentication.onlineuser.first_name.read',
    'authentication.onlineuser.last_name.read',
    'authentication.onlineuser.email.read',
    'authentication.onlineuser.is_member.read',
    'authentication.onlineuser.is_staff.read',
    'authentication.onlineuser.is_superuser.read',
    'authentication.onlineuser.field_of_study.read',
    'authentication.onlineuser.nickname.read',
    'authentication.onlineuser.rfid.read'
]


@protected_resource(SCOPES)
def user(request):
    """
    Basic user information provided based on the Bearer Token provided by an SSO application
    :param request: The Django Request object
    :return: An HTTP response
    """

    try:
        bearer = request.META.get('HTTP_AUTHORIZATION', '')
        bearer = bearer.split(' ')
        if len(bearer) != 2:
            return JsonResponse(status=403, data={'error': 'Unauthorized'})

        bearer = bearer[1]
        tokenobject = AccessToken.objects.get(token=bearer)
        userdata = {
            'first_name': tokenobject.user.first_name,
            'last_name': tokenobject.user.last_name,
            'username': tokenobject.user.username,
            'email': tokenobject.user.get_email().email,
            'member': tokenobject.user.is_member,
            'staff': tokenobject.user.is_staff,
            'superuser': tokenobject.user.is_superuser,
            'nickname': tokenobject.user.nickname,
            'rfid': tokenobject.user.rfid,
            'image': tokenobject.user.get_image_url(),
            'field_of_study': tokenobject.user.get_field_of_study_display(),
        }

        return JsonResponse(status=200, data=userdata)
    except AccessToken.DoesNotExist:
        return JsonResponse(status=403, data={'error': 'Unauthorized'})
