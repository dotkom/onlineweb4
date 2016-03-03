# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('splash', '0002_splashyear_start_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='splashyear',
            options={'ordering': ('-start_date',)},
        ),
    ]
