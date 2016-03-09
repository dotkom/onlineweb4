# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_jobmail_set_true'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='committee',
            field=models.CharField(default=b'hs', max_length=10, verbose_name='komite', choices=[(b'hs', 'Hovedstyret'), (b'appkom', 'Applikasjonskomiteen'), (b'arrkom', 'Arrangementskomiteen'), (b'bankom', 'Bank- og \xf8konomikomiteen'), (b'bedkom', 'Bedriftskomiteen'), (b'dotkom', 'Drifts- og utviklingskomiteen'), (b'ekskom', 'Ekskursjonskomiteen'), (b'fagkom', 'Fag- og kurskomiteen'), (b'jubkom', 'Jubileumskomiteen'), (b'pangkom', 'Pensjonistkomiteen'), (b'prokom', 'Profil-og aviskomiteen'), (b'trikom', 'Trivselskomiteen'), (b'velkom', 'Velkomstkomiteen'), (b'redaksjonen', 'Redaksjonen')]),
            preserve_default=True,
        ),
    ]
