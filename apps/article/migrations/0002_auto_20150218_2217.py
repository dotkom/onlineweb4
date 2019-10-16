# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='changed_by',
            field=models.ForeignKey(related_name='changed_by', editable=False, to=settings.AUTH_USER_MODEL, verbose_name='endret av', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', editable=False, to=settings.AUTH_USER_MODEL, verbose_name='opprettet av', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
