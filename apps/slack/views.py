from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.slack.serializers import SlackSerializer
from apps.slack.utils import SlackException, SlackInvite


class InviteViewSet(ViewSet):
    serializer_class = SlackSerializer

    def create(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        slack = SlackInvite()
        try:
            slack.invite(request.data['email'])
        except SlackException as e:
            raise serializers.ValidationError({'detail': str(e)})

        return Response()
