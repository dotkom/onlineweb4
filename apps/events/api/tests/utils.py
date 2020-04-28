from django_dynamic_fixture import G

from apps.authentication.models import OnlineUser
from apps.events.tests.utils import attend_user_to_event


def generate_attendee(event, username, rfid):
    user = G(OnlineUser, username=username, rfid=rfid)
    return attend_user_to_event(event, user)


def generate_valid_rfid():
    return "12345678"
