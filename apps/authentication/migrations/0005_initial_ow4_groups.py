# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from onlineweb4.settings import PROJECT_ROOT_DIRECTORY

import json

class Migration(migrations.Migration):

    def create_ow4_groups(apps, schema_editor):
        # Get the model in case it's edited by some other migrations
        Group = apps.get_model('auth', 'Group')

        try:
            file_location = PROJECT_ROOT_DIRECTORY + '/files/data_migrations/auth/groups_per_20150415.json'
            with open(file_location, 'rb') as f:
                groups = json.loads(f.read())

                for group in groups:
                    try:
                        # Try to get the group by ID first
                        if Group.objects.filter(id=group['pk']).count() > 0:
                            # Group id exists, cannot create group
                            continue
                        elif Group.objects.filter(name=group['fields']['name']).count() > 0:
                            # Group name exists, cannot create group
                            continue
                    except Group.DoesNotExist:
                        pass
                    finally:
                        new_group = Group()
                        new_group.id = group['pk']
                        new_group.name = group['fields']['name']
                        new_group.save()


        except IOError:
            self.stdout.write('File not found')

    dependencies = [
        ('authentication', '0004_onlineuser_online_mail'),
    ]

    operations = [
        migrations.RunPython(create_ow4_groups)
    ]
