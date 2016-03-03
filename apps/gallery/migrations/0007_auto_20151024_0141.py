# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0006_auto_20151018_0707'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unhandledimage',
            options={'verbose_name': 'Ubehandlet bilde', 'verbose_name_plural': 'Ubehandlede bilder', 'permissions': (('view_unhandledimage', 'View UnhandledImage'),)},
        ),
    ]
