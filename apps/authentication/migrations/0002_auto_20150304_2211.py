# -*- coding: utf-8 -*-


import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sso', '0002_auto_20171127_1304'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineuser',
            name='started_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='startet studie'),
            preserve_default=True,
        ),
    ]
