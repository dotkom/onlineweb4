from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from utils.pagination import PageNumberPagination

from .filters import CareerOpportunityFilter
from .models import CareerOpportunity
from .serializers import CareerSerializer


def index(request, id=None):
    return render(request, "careeropportunity/index.html")


class HundredItemsPaginator(PageNumberPagination):
    """
    Default page size to 100 items per page for backwards compatibility.
    # TODO: Remove backwards compatible 100 items per page when replacing OW4 frontend with OWF.
    """

    page_size = 100
    max_page_size = 100


class CareerViewSet(viewsets.ModelViewSet):
    queryset = CareerOpportunity.objects.all()
    serializer_class = CareerSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = HundredItemsPaginator
    filterset_class = CareerOpportunityFilter

    def get_queryset(self, *args, **kwargs):
        now = timezone.now()
        # TODO: allow viewing old career opportunities after they have ended when new front-end is ready.
        return (
            super()
            .get_queryset()
            .filter(start__lte=now, end__gte=now)
            .order_by("-featured", "-start")
        )
