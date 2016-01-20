# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermixin',
            name='assigned_to',
            field=models.ForeignKey(related_name='assigned_to', verbose_name='tilordnet til', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='ordermixin',
            name='ordered_by',
            field=models.ForeignKey(related_name='ordered_by', verbose_name='bestilt av', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ordermixin',
            name='ordered_committee',
            field=models.ForeignKey(related_name='ordered_committee', verbose_name='bestilt av komite', to='auth.Group'),
        ),
    ]
