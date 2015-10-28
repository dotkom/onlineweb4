# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0005_responsiveimage_image_wide'),
        ('article', '0003_auto_20151018_0311'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='image',
            field=models.ForeignKey(default=None, to='gallery.ResponsiveImage', null=True),
            preserve_default=True,
        ),
    ]
