# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_auto_20150916_1953'),
        ('companyprofile', '0002_auto_20151014_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='image',
            field=models.ForeignKey(to='gallery.ResponsiveImage', default=None, to_field='Bilde'),
            preserve_default=True,
        ),
    ]
