# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20151014_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='committee',
            field=models.CharField(default=b'hs', max_length=10, verbose_name='komite', choices=[(b'hs', 'Hovedstyret'), (b'appkom', 'Applikasjonskomiteen'), (b'arrkom', 'Arrangementskomiteen'), (b'bankom', 'Bank- og \xf8konomikomiteen'), (b'bedkom', 'Bedriftskomiteen'), (b'dotkom', 'Drifts- og utviklingskomiteen'), (b'ekskom', 'Ekskursjonskomiteen'), (b'fagkom', 'Fag- og kurskomiteen'), (b'jubkom', 'Jubileumskomiteen'), (b'pangkom', 'Pensjonistkomiteen'), (b'prokom', 'Profil-og aviskomiteen'), (b'redaksjonen', 'Redaksjonen'), (b'trikom', 'Trivselskomiteen'), (b'velkom', 'Velkomstkomiteen')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='position',
            name='position',
            field=models.CharField(default=b'medlem', max_length=10, verbose_name='stilling', choices=[(b'medlem', 'Medlem'), (b'leder', 'Leder'), (b'nestleder', 'Nestleder'), (b'redaktor', 'Redakt\xf8r'), (b'okoans', '\xd8konomiansvarlig')]),
            preserve_default=True,
        ),
    ]
