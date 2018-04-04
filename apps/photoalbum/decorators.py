# -*- coding: utf-8 -*-

from middleware.http import Http403
from apps.photoalbum.utils import is_prokom

from django.core.exceptions import PermissionDenied

def prokom_required(view_func):

	def is_prokom(request, *args, **kwargs):
		print("Request: ", request)
		print("View_func: ", view_func)
		prokom = False
		if prokom:
			return view_func(request, *args, **kwargs)
		raise PermissionDenied
		
	return is_prokom