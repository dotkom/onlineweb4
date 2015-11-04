# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


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
