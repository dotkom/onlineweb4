# -*- coding: utf-8 -*-

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
        print("Is not a member")
        raise Http403
    return check_membership
