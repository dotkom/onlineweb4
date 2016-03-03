# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_auto_20151014_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='added_date',
            field=models.DateTimeField(auto_now=True, verbose_name='opprettet dato'),
        ),
    ]
