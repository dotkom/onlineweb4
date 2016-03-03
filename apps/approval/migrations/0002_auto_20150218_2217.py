# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('approval', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='approval',
            name='applicant',
            field=models.ForeignKey(related_name='applicant', editable=False, to=settings.AUTH_USER_MODEL, verbose_name='s\xf8ker'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='approval',
            name='approver',
            field=models.ForeignKey(related_name='approver', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='godkjenner'),
            preserve_default=True,
        ),
    ]
