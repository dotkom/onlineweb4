# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupRestriction',
            fields=[
                ('event', models.OneToOneField(related_name='group_restriction', primary_key=True, serialize=False, to='events.Event', on_delete=models.CASCADE)),
                ('groups', models.ManyToManyField(help_text='Legg til de gruppene som skal ha tilgang til arrangementet', to='auth.Group', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'restriksjon',
                'verbose_name_plural': 'restriksjoner',
                'permissions': (('view_restriction', 'View Restriction'),),
            },
            bases=(models.Model,),
        ),
    ]
