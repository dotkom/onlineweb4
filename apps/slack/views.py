from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

class InviteViewSet(ViewSet):
    def create(self, request, format=None):
        return Response(request.data)
