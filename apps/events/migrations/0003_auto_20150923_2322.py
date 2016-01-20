# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150923_1929'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extras',
            options={'ordering': ['choice'], 'verbose_name': 'ekstra valg', 'verbose_name_plural': 'ekstra valg', 'permissions': (('add_extras', 'Add Extras'),)},
        ),
        migrations.AddField(
            model_name='attendee',
            name='extras',
            field=models.ForeignKey(blank=True, to='events.Extras', null=True),
            preserve_default=True,
        ),
    ]
