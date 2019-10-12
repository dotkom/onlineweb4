# -*- coding: utf-8 -*-
from apps.photoalbum.tasks import send_report_on_photo


def report_photo(description, photo, user):
    send_report_on_photo(user, photo, description)
