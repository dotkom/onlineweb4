# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('careeropportunity', '0002_auto_20151017_0250'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='careeropportunity',
            options={'verbose_name': 'karrieremulighet', 'verbose_name_plural': 'karrieremuligheter', 'permissions': (('view_careeropportunity', 'View CareerOpportunity'),)},
        ),
    ]
