from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import RequestContext

from apps.genfors.models import Meeting

import datetime


@login_required
def genfors(request):
	context = {}
	today = datetime.date.today()

	meetings = Meeting.objects.filter(start_date__range=[today, today + datetime.timedelta(days=1)])
	if meetings:
		meeting = meetings[0]
		context['meeting'] = meeting
	return render(request, "genfors/index.html", context)


@login_required
def admin(request):
	context = {}
	return render(request, "genfors/index.html", context)
