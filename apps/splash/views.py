from django.http import Http404
from django.shortcuts import render
from apps.splash.models import SplashYear

from apps.events.utils import SplashCalendar


def index(request):
    splash_year = SplashYear.objects.current()
    if not splash_year:
        raise Http404

    splash_year.events = _merge_events(splash_year.events())

    return render(request, 'splash/base.html', {'splash_year': splash_year})


def calendar_export(request):
    calendar = SplashCalendar()
    calendar.events()
    return calendar.response()


# And I'm really sorry for this ...
def _merge_events(splash_events):
    events = []

    for event in splash_events:
        if len(events) > 0 and event.start_time.strftime('%d-%m') == events[-1][0].start_time.strftime('%d-%m'):
            events[-1].append(event)
        else:
            events.append([event])

    return events
