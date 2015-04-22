from django.shortcuts import render
from django.utils import timezone
from apps.splash.models import SplashEvent, SplashYear


def index(request):
    splash_year = SplashYear.objects.filter(start_date__gte=timezone.now())[0]
    return render(request, 'splash/base.html', {'splash_year': splash_year })
