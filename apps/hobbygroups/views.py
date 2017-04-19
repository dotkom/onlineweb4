from django.shortcuts import render_to_response
from django.template import RequestContext


# Index page
def index(request):
    return render_to_response('hobbygroups/index.html', context_instance=RequestContext(request))
