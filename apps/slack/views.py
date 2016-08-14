from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import serializers

from apps.slack.utils import SlackException, SlackInvite


class InviteViewSet(ViewSet):
    def create(self, request, format=None):
        if not('email' in request.data and 'name' in request.data):
            raise serializers.ValidationError('Missing name or e-mail')
        slack = SlackInvite()
        try:
            slack.invite(request.data['email'], request.data['name'])
        except SlackException as e:
            raise serializers.ValidationError(str(e))

        return Response()
