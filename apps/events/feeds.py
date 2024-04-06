from django.contrib.syndication.views import Feed
from django.db.models.functions import Now
from django.utils.feedgenerator import Atom1Feed

from apps.events.models.Attendance import AttendanceEvent


class OpenedSignupsFeed(Feed):
    feed_type = Atom1Feed
    title = "Event påmelding"
    link = "/signup-feed/"
    description = "Påmeldinger som har nylig åpnet"

    def items(self):
        return (
            AttendanceEvent.objects.select_related("event")
            .filter(
                registration_start__lte=Now(),
                event__visible=True,
                event__group_restriction__isnull=True,
            )
            .order_by("-registration_start")[:5]
        )

    def item_title(self, item: AttendanceEvent):
        return item.event.title

    def item_description(self, item: AttendanceEvent):
        return f"Påmelding for {item.event.title} har åpnet!"

    def item_pubdate(self, item: AttendanceEvent):
        return item.registration_start

    def item_link(self, item):
        return f"https://online.ntnu.no/events/{item.pk}"
