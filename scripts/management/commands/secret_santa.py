# -*- coding: utf-8 -*-

import random

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

from apps.events.models import AttendanceEvent


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('event_id')


    def handle(self, *args, **options):
        event_id = options['event_id']
        event = AttendanceEvent.objects.get(event=event_id)
        users = event.attendees_qs
        random_users = Command.generate_random_list(users)
        to_from_dict = {}
        for count, user in enumerate(users):
            to_from_dict['Par %s' % (count+1)] = {'To': user.user.get_full_name(), 'From': users[random_users[count]].user.get_full_name()}
            
            Command.send_mail(user, users[random_users[count]])

        Command.mail_to_committee(to_from_dict)


    # Function for generating a list with random numbers corresponding to
    # the indexes of the list of users attending the event.
    def generate_random_list(users):
        to_from = random.sample(range(0, len(users)), len(users))
        while(not Command.check_random_list(to_from)):
            to_from = random.sample(range(0, len(users)), len(users))
        return to_from


    # Function for checking that the random list of indexes is valid.
    # Checks the index of the original list of users against the randomly
    # generated number. If index and random number is the same, then someone
    # got themselves as secret Santa.
    def check_random_list(random):
        for count, user in enumerate(random):
            if (count == random[count]):
                return False
        return True


    def send_mail(user_to, user_from):
        subject = "Secret santa"

        content = render_to_string('secret_santa/attendee_mail.txt', {
            'user_to': user_to.user.get_full_name(),
            'mail_committee': settings.EMAIL_TRIKOM,
        })

        receiver = user_from.user.email

        EmailMessage(subject, content, settings.EMAIL_TRIKOM, [receiver]).send()


    def mail_to_committee(to_from_dict):
        subject = "Secret santa til-fra liste"

        content = render_to_string('secret_santa/committee_mail.txt', {
            'to_from_dict': to_from_dict,
        })

        EmailMessage(subject, content, settings.EMAIL_TRIKOM, [settings.EMAIL_TRIKOM]).send()
