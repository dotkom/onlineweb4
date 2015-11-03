# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_auto_20150623_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackrelation',
            name='answered',
            field=models.ManyToManyField(related_name='feedbacks', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
