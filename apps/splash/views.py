import datetime
from django.shortcuts import render
from apps.splash.models import SplashEvent, SplashYear


def index(request):
    # I'm really sorry ...
    splash_year = SplashYear.objects.get(start_date__gt=str(datetime.date.today() - datetime.timedelta(180)))

    splash_year.events = _merge_events(splash_year.splash_events.all())

    return render(request, 'splash/base.html', {'splash_year': splash_year })


# And I'm really sorry for this ...
def _merge_events(splash_events):
    events = []

    for event in splash_events:
        if len(events) > 0 and event.start_time.strftime('%d-%m') == events[-1][0].start_time.strftime('%d-%m'):
            events[-1].append(event)
        else:
            events.append([event])

    return events
