from apps.splash.utils import SplashCalendar


def calendar_export(request):
    calendar = SplashCalendar()
    calendar.events()
    return calendar.response()
