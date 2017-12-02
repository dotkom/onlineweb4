# -*- coding: utf-8 -*-

import os
import random

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from apps.events.models import AttendanceEvent


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('event_id')

    def handle(self, *args, **options):
        event_id = options['event_id']
        event = AttendanceEvent.objects.get(event=event_id)
        users = event.attendees_qs
        random_users = self.generate_random_list(users)
        to_from_dict = {}
        for count, user in enumerate(users):
            to_from_dict['Par %s' % (count+1)] = {'To': user.user.get_full_name(),
                                                  'From': users[random_users[count]].user.get_full_name()}
            self.send_mail(user, users[random_users[count]])

        self.write_to_file(to_from_dict)
        self.mail_to_committee()

    # Function for generating a list with random numbers corresponding to
    # the indexes of the list of users attending the event.
    @staticmethod
    def generate_random_list(users):
        to_from = random.sample(range(len(users)), len(users))
        to_from = tuple([0, 1, 2, 3, 4, 5, 6, 7])
        return_list = Command.fix_random_list(list(to_from))
        print(to_from)
        print(return_list)
        return return_list

    # Function for checking that the random list of indexes is valid.
    # Checks the index of the original list of users against the randomly
    # generated number. If index and random number is the same, then someone
    # got themselves as secret Santa.
    @staticmethod
    def fix_random_list(random_list):
        random_list = list(random_list)
        for user_index, user in enumerate(random_list):
            # The user part of the for-loop does not update when the random_list
            # is updated. So to avoid swapping an already swapped item the index
            # must be checked against the updated list, not the user created in the
            # beginning of the loop.
            if user_index == random_list[user_index]:
                random_list = Command.swap_pair(random_list, user_index)
        return random_list

    @staticmethod
    def swap_pair(random_list, user_index):
        random_list = list(random_list)
        user_swap_index = random.choice(random_list)
        if user_swap_index == user_index:
            if user_swap_index != len(random_list)-1:
                user_swap_index += 1
            else:
                user_swap_index -= 1
        random_list[user_index], random_list[user_swap_index] = \
            random_list[user_swap_index], random_list[user_index]
        return random_list

    @staticmethod
    def send_mail(user_to, user_from):
        subject = "Secret santa"

        content = render_to_string('secret_santa/attendee_mail.txt', {
            'user_to': user_to.user.get_full_name(),
            'mail_committee': settings.EMAIL_TRIKOM,
        })

        receiver = user_from.user.email

        EmailMessage(subject, content, settings.EMAIL_TRIKOM, [receiver]).send()

    @staticmethod
    def mail_to_committee():
        subject = "Secret santa e-post sendt til påmeldte"

        content = render_to_string('secret_santa/committee_mail.txt')

        EmailMessage(subject, content, settings.EMAIL_TRIKOM, [settings.EMAIL_TRIKOM]).send()

    @staticmethod
    def write_to_file(to_from_dict):
        directory = 'uploaded_media/txt'
        if not os.path.exists(directory):
            os.makedirs(directory)

        txt_file = open(directory + '/secret_santa_to_from.txt', 'w+')

        content = render_to_string('secret_santa/to_from_list.txt', {
            'to_from_dict': to_from_dict,
        })

        txt_file.write(content)
        txt_file.close()
