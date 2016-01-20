# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_grouprestriction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldofstudyrule',
            name='field_of_study',
            field=models.SmallIntegerField(verbose_name='studieretning', choices=[(0, 'Gjest'), (1, 'Bachelor i Informatikk (BIT)'), (10, 'Programvaresystemer (P)'), (11, 'Databaser og s\xf8k (DS)'), (12, 'Algoritmer og datamaskiner (AD)'), (13, 'Spillteknologi (S)'), (14, 'Kunstig intelligens (KI)'), (15, 'Helseinformatikk (MSMEDTEK)'), (30, 'Annen mastergrad'), (80, 'PhD'), (90, 'International'), (100, 'Annet Onlinemedlem')]),
            preserve_default=True,
        ),
    ]
