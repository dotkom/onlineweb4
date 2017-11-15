from django.shortcuts import render
from rest_framework import viewsets


from apps.hobbygroups.models import Hobby
from apps.hobbygroups.serializers import HobbySerializer


# Index page
def index(request):
    hobbygroups = Hobby.objects.all().order_by('-priority')
    context = {
        'hobbygroups': hobbygroups,
    }
    return render(request, 'hobbygroups/index.html', context)


class HobbyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer
