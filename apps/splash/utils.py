import icalendar
from django.utils import timezone

from apps.events.utils import Calendar
from apps.splash.models import SplashEvent


class SplashCalendar(Calendar):
    def add_event(self, event):
        cal_event = icalendar.Event()
        cal_event.add("dtstart", event.start_time)
        cal_event.add("dtend", event.end_time)
        cal_event.add("summary", event.title)
        cal_event.add("description", event.content)
        cal_event.add("uid", "splash-" + str(event.id) + "@online.ntnu.no")

        self.cal.add_component(cal_event)

    def events(self):
        self.add_events(
            SplashEvent.objects.filter(start_time__year=timezone.now().year)
        )
        self.filename = "events"
