# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marks', '0002_auto_20150415_2348'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suspension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255, verbose_name='beskrivelse')),
                ('active', models.BooleanField(default=False)),
                ('added_date', models.DateTimeField(auto_now=True)),
                ('expiration_date', models.DateField(verbose_name='utl\xf8psdato', null=True, editable=False, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
