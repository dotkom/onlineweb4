# -*- coding: utf-8 -*-

import logging
import hashlib

from rest_framework import filters, mixins, permissions, response, viewsets

from django.shortcuts import render
from apps.authentication.models import OnlineUser
from django.contrib.auth.models import User

from apps.profiles.serializers import PrivacySerializer, PublicProfileSerializer
from apps.lillebror.serializers import ProfileSerializer


class all_user_data(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, format=None):
        logger = logging.getLogger(__name__)
        # username = '22'
        # email = 'annon@ema.il'
        # password = 'thisisapassword'
        # user = OnlineUser.objects.create_user(username=username, email=email, password=password)
        # user_pk = user.pk
        # user.groups.set(request.user.groups.all())
        # user.user_permissions.set(request.user.user_permissions.all())
        user = request.user
        user = OnlineUser.objects.get(username='1')
        logger.warning(user.username)
        # user.pk = user_pk
        # user.username = username
        # user.password = password
        # user.ntnu_username = ''
        # user.save()

        serializer = ProfileSerializer(user)
        return response.Response(serializer.data)


class RemoveUserDataAsDelete(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, requset, format=None):
        user = requset.user
        serializer = ProfileSerializer(user)
        return response.Response(serializer.data)

    def put(self, requset, format=None):
        logger = logging.getLogger(__name__)
        user = OnlineUser.objects.get(username='1')
        logger.warning(user.username)
        user.username = hashlib.sha256(str(user.username).encode('utf-8')).hexdigest()
        logger.warning(user.username)
        user.email = 'deleted@user.mail'
        user.password = 'ThisUserHasBeenDeleted'
        # user.groups.clear()
        # user.user_permissions.clear()
        user.ntnu_username = 'deleted'
        serializer = ProfileSerializer(data=ProfileSerializer(user).data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user)
            return response.Response(serializer.data)
