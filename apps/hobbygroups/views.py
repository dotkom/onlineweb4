from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.hobbygroups.models import Hobby


# Index page
def index(request):
    hobbygroups = Hobby.objects.all()
    context = {
        'hobbygroups': hobbygroups,
    }
    return render_to_response('hobbygroups/index.html', context, context_instance=RequestContext(request))
