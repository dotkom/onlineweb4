# -*- coding: utf-8 -*-

import os

from django.contrib.auth.models import User, Group
from django.core.management.base import NoArgsCommand

from onlineweb.management_scripts.mail.maillists import update_list_memberships
from onlineweb.settings import MAILLISTS_STORAGE_PATH

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):
        def user_emails(users):
            return [user.email for user in users]

        # UserProfile.FIELD_OF_STUDY_CHOICES = ((1, 'BIT'), (2, 'MIT'), (3, 'ÅIT'), (4, 'PhD'), (5, 'LUR'), (6, 'BISK'), (7, 'Gjest'),)
        users = User.objects.filter(is_active=True)
        groups = Group.objects.all().exclude(name__iexact='pangkom')

        lists = {
            'all': user_emails(users),
            'info' : user_emails(users.filter(userprofile__want_mail=True)),
            'arsstudium': user_emails(users.filter(userprofile__field_of_study=3)),
            'bachelor' : user_emails(users.filter(userprofile__field_of_study=1)),
            'master' : user_emails(users.filter(userprofile__field_of_study=2)),
            'bachelor1' : [],
            'bachelor2' : [],
            'bachelor3' : [],
            'master1' : [],
            'master2' : []
        }

        lists['all'].append('dotkombot@dworek.online.ntnu.no')
        lists['info'].append('dotkombot@dworek.online.ntnu.no')
        lists['arsstudium'].append('dotkombot@dworek.online.ntnu.no')
        lists['bachelor'].append('dotkombot@dworek.online.ntnu.no')
        lists['master'].append('dotkombot@dworek.online.ntnu.no')

        for user in users.filter(userprofile__field_of_study=1):
            profile = user.get_profile()
            lists['bachelor' + str(profile.year)].append(user.email)

        for user in users.filter(userprofile__field_of_study=2):
            profile = user.get_profile()

            if(profile.year == 4):
                lists['master1'].append(user.email)
            elif(profile.year == 5):
                lists['master2'].append(user.email)

        for group in groups:
            list_name = group.name.lower()
            lists[list_name] = user_emails(group.user_set.all())
            if list_name in ('dotkom', 'komiteer'):
                lists[list_name].append('dotkombot@dworek.online.ntnu.no')

            if not list_name == 'hovedstyret':
                lists[list_name].append('leder@online.ntnu.no')
                lists[list_name].append('nestleder@online.ntnu.no')

        for list_name, emails in lists.items():
            persist_list(list_name, emails)

def open_list_file(path, list_name, mode):
    return open(os.path.join(path, list_name), mode)

def persist_list(list_name, emails):
    list_file = open_list_file(MAILLISTS_STORAGE_PATH, list_name, mode='w')
    for email in emails:
        list_file.write(email.encode('UTF-8') + '\n')
    list_file.close()

    print 'Wrote %d emails to list : %s' % (len(emails), list_name)
