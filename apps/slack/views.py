from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import serializers

from apps.slack.utils import SlackException, SlackInvite
from apps.slack.serializers import SlackSerializer


class InviteViewSet(ViewSet):
    serializer_class = SlackSerializer

    def create(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        slack = SlackInvite()
        try:
            slack.invite(request.data['email'], request.data['name'])
        except SlackException as e:
            raise serializers.ValidationError(str(e))

        return Response()
