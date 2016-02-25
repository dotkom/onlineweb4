# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='changed_by',
            field=models.ForeignKey(related_name='changed_by', editable=False, to=settings.AUTH_USER_MODEL, verbose_name='endret av'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', editable=False, to=settings.AUTH_USER_MODEL, verbose_name='opprettet av'),
            preserve_default=True,
        ),
    ]
