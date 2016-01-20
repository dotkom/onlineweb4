# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20150328_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='instant_payment',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='multiple_description',
        ),
        migrations.AddField(
            model_name='payment',
            name='delay',
            field=models.SmallIntegerField(null=True, verbose_name='utsettelse', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_type',
            field=models.SmallIntegerField(default=1, verbose_name='type', choices=[(1, 'Umiddelbar'), (2, 'Frist'), (3, 'Utsettelse')]),
            preserve_default=False,
        ),
    ]
