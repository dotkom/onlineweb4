from django.shortcuts import render
from onlineweb4.permissions import ModelPermission
from rest_framework import viewsets

from apps.hobbygroups.models import Hobby
from apps.hobbygroups.serializers import HobbySerializer


# Index page
def index(request):
    hobbygroups = Hobby.objects.filter(active=True).order_by("-priority")
    context = {"hobbygroups": hobbygroups}
    return render(request, "hobbygroups/index.html", context)


class HobbyPermission(ModelPermission):
    create_permissions = ["hobbygroups.create_hobby"]
    update_permissions = ["hobbygroups.update_hobby"]
    delete_permissions = ["hobbygroups.delete_hobby"]


class HobbyViewSet(viewsets.ModelViewSet):
    queryset = Hobby.objects.filter(active=True)
    serializer_class = HobbySerializer
    permission_classes = (HobbyPermission,)
