import logging

from django.shortcuts import render
from apps.authentication.models import OnlineUser as User


def all_user_data(request):
    logger = logging.getLogger(__name__)

    return(render(request, None))
