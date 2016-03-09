# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldofstudyanswer',
            name='answer',
            field=models.SmallIntegerField(verbose_name='Studieretning', choices=[(0, 'Gjest'), (1, 'Bachelor i Informatikk (BIT)'), (10, 'Programvaresystemer (P)'), (11, 'Databaser og s\xf8k (DS)'), (12, 'Algoritmer og datamaskiner (AD)'), (13, 'Spillteknologi (S)'), (14, 'Kunstig intelligens (KI)'), (15, 'Helseinformatikk (MSMEDTEK)'), (30, 'Annen mastergrad'), (80, 'PhD'), (90, 'International'), (100, 'Annet Onlinemedlem')]),
            preserve_default=True,
        ),
    ]
