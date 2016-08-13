from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from apps.slack.utils import SlackException, SlackInvite

class InviteViewSet(ViewSet):
    def create(self, request, format=None):
        if not('email' in request.data and 'name' in request.data):
            return Response({
                'ok': False,
                'error': 'Missing name or e-mail'
            })
        slack = SlackInvite()
        try:
            slack.invite(request.data['email'], request.data['name'])
        except SlackException as e:
            return Response({
                'ok': False,
                'error': str(e)
            })

        return Response({
            'ok': True
        })
