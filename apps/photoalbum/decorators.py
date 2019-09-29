# -*- coding: utf-8 -*-


from django.core.exceptions import PermissionDenied
from middleware.http import Http403

from apps.photoalbum.utils import is_prokom


def prokom_required(view_func):

    def check_if_is_prokom(request, *args, **kwargs):
        is_prokom(request.user)
        prokom = True
        if prokom:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied

    return check_if_is_prokom
