from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import UserSerializer


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    Viewset for User serializer. Supports filtering on 'first_name', 'last_name', 'email'
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    filter_fields = ('first_name', 'last_name', 'rfid',)
