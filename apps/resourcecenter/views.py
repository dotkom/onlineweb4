from django.shortcuts import render
from rest_framework import viewsets

from apps.resourcecenter.models import Resource
from apps.resourcecenter.serializers import ResourceSerializer
from onlineweb4.permissions import ModelPermission


# Index page
def index(request):
    resources = Resource.objects.all().order_by("-priority")
    context = {"resources": resources}
    return render(request, "resourcecenter/index.html", context)


class ResourcePermission(ModelPermission):
    create_permissions = ["resourcecenter.create_resource"]
    update_permissions = ["resourcecenter.update_resource"]
    delete_permissions = ["resourcecenter.delete_resource"]


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (ResourcePermission,)
