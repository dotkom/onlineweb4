# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20150923_2322'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extras',
            options={'ordering': ['choice'], 'verbose_name': 'ekstra valg', 'verbose_name_plural': 'ekstra valg'},
        ),
    ]
