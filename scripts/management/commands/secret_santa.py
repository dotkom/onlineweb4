# -*- coding: utf-8 -*-

import random

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage

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
        #to_from_dict_user = {}
        for count, user in enumerate(users):
            to_from_dict['Par %s' % (count+1)] = {'To': user.user.first_name + ', ' + user.user.last_name, 
                'from': users[random_users[count]].user.first_name + ', ' + users[random_users[count]].user.last_name}
            
            Command.send_mail(user, users[random_users[count]])

        Command.mail_to_committee(to_from_dict)


    def generate_random_list(users):
        to_from = random.sample(xrange(0, len(users)), len(users))
        while(not Command.check_random_list(to_from)):
            to_from = random.sample(xrange(0, len(users)), len(users))
        return to_from


    def check_random_list(random):
        for count, user in enumerate(random):
            if (count == random[count]):
                return False
        return True


    def send_mail(user_to, user_from):
        committee_mail = "trikom@online.ntnu.no"
        subject = "Secret santa"

        message = "Hei."
        message += "\nDu har blitt tildelt " + user_to.user.first_name + ' ' + user_to.user.last_name + " som du skal være secret santa for"
        message += "\n\nDersom du har spørsmål kan du sende mail til " + committee_mail
        message += "\n\nMvh\nLinjeforeningen Online"

        receiver = user_from.user.email

        EmailMessage(subject, str(message), committee_mail, [receiver]).send()


    def mail_to_committee(to_from_dict):
        committee_mail = "trikom@online.ntnu.no"
        subject = "Secret santa til-fra liste"

        message = "Secret santa til og fra liste:"

        for key, value in to_from_dict.items():
            message += '\n' + str(key) + str(value)

        EmailMessage(subject, str(message), committee_mail, [committee_mail]).send()
