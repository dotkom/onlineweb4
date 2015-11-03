# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendanceevent',
            name='extras',
            field=models.ManyToManyField(to='events.Extras', blank=True),
        ),
        migrations.AlterField(
            model_name='grouprestriction',
            name='groups',
            field=models.ManyToManyField(help_text='Legg til de gruppene som skal ha tilgang til arrangementet', to='auth.Group', blank=True),
        ),
    ]
