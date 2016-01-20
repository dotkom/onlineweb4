# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Privacy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visible_for_other_users', models.BooleanField(default=True, verbose_name='profil synlig for andre brukere')),
                ('expose_nickname', models.BooleanField(default=True, verbose_name='vis kallenavn')),
                ('expose_email', models.BooleanField(default=True, verbose_name='vis epost')),
                ('expose_phone_number', models.BooleanField(default=True, verbose_name='vis telefonnummer')),
                ('expose_address', models.BooleanField(default=True, verbose_name='vis addresse')),
                ('user', models.ForeignKey(related_name='privacy', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'verbose_name': 'personvern',
                'verbose_name_plural': 'personvern',
                'permissions': (('view_privacy', 'View Privacy'),),
            },
            bases=(models.Model,),
        ),
    ]
