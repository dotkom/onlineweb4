# -*- coding: utf-8 -*-

from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden
from django.utils.decorators import available_attrs

from middleware.http import Http403

def need_membership(view_func):
    """
    Simple decorator to show whether or not a user is a 
    valid member of Online.
    """
    def check_membership(request, *args, **kwargs):
        if request.user.is_member:
            return view_func(request, *args, **kwargs)
        # Raise 403 error if user does not have access
        raise Http403
    return check_membership
