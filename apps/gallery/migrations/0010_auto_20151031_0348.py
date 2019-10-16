# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0009_responsiveimage_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsiveimage',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text=b'En komma eller mellomrom-separert liste med tags.', verbose_name='Tags'),
        ),
    ]
