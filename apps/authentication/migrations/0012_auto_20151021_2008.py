# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlineuser',
            name='github',
            field=models.URLField(null=True, verbose_name='github', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='onlineuser',
            name='linkedin',
            field=models.URLField(null=True, verbose_name='linkedin', blank=True),
            preserve_default=True,
        ),
    ]
