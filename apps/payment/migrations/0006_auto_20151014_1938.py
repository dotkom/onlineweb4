# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20150429_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='added_date',
            field=models.DateTimeField(auto_now=True, verbose_name='opprettet dato', auto_now_add=True),
            preserve_default=True,
        ),
    ]
