# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20150311_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlineuser',
            name='online_mail',
            field=models.CharField(max_length=50, null=True, verbose_name='Online-epost', blank=True),
            preserve_default=True,
        ),
    ]
