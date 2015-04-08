# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0005_auto_20150318_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poster',
            name='company',
            field=models.ForeignKey(related_name='bedrift', blank=True, to='companyprofile.Company', null=True),
            preserve_default=True,
        ),
    ]
