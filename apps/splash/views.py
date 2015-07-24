from django.shortcuts import render
from datetime
from apps.splash.models import SplashEvent, SplashYear


def index(request):
    # I'm really sorry ...
    splash_year = SplashYear.objects.filter(start_date__gt=str(datetime.date.today() - datetime.timedelta(180)))
    return render(request, 'splash/base.html', {'splash_year': splash_year })
