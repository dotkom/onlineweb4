from django.shortcuts import redirect
from rest_framework import viewsets

from apps.hobbygroups.models import Hobby
from apps.hobbygroups.serializers import HobbySerializer
from onlineweb4.permissions import ModelPermission


def index(request):
    return redirect("https://online.ntnu.no/hobbygroups", permanent=True)


class HobbyPermission(ModelPermission):
    create_permissions = ["hobbygroups.create_hobby"]
    update_permissions = ["hobbygroups.update_hobby"]
    delete_permissions = ["hobbygroups.delete_hobby"]


class HobbyViewSet(viewsets.ModelViewSet):
    queryset = Hobby.objects.filter(active=True)
    serializer_class = HobbySerializer
    permission_classes = (HobbyPermission,)
