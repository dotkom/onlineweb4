# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20150304_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineuser',
            name='started_date',
            field=models.DateField(default=datetime.date.today, verbose_name='startet studie'),
            preserve_default=True,
        ),
    ]
