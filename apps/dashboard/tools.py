# -*- encoding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

def has_access(request):
    """
    This helper method does a basic check to see if the logged in user
    has access to the dashboard.
    """

    if request.user.is_superuser:
        return True
    
    try:
        committees = Group.objects.get(name='Komiteer')
    except ObjectDoesNotExist:
        committees = None

    if committees and committees in request.user.groups.all():
        return True

    return False

