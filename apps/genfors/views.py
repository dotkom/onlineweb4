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
        if meeting.get_active_question():
            aq = meeting.get_active_question()
            context['active_question'] = {}
            context['active_question']['total_votes'] = aq.get_votes().count()
            res = aq.get_results()
            if aq.question_type == 0:
                context['active_question']['yes_percent'] = res['JA'] * 100 / context['active_question']['total_votes']
                context['active_question']['no_percent'] = res['NEI'] * 100 / context['active_question']['total_votes']
                context['active_question']['blank_percent'] = res['BLANKT'] * 100 / context['active_question']['total_votes']
            else:
                context['active_question']['multiple_choice']
                context['active_question']['multiple_choice'] = [sum(res[r] * 100 / context['active_question']['total_votes']) for r in res]
        
	return render(request, "genfors/index.html", context)


@login_required
def admin(request):
	context = {}
	return render(request, "genfors/index.html", context)
