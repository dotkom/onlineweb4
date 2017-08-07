from django.shortcuts import render

from apps.hobbygroups.models import Hobby


# Index page
def index(request):
    hobbygroups = Hobby.objects.all().order_by('-hobby_priority')
    context = {
        'hobbygroups': hobbygroups,
    }
    return render(request, 'hobbygroups/index.html', context)
