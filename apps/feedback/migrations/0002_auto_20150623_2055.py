# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratinganswer',
            name='answer',
            field=models.SmallIntegerField(default=0, verbose_name='karakter', choices=[(b'', b''), (1, b'1'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5'), (6, b'6')]),
            preserve_default=True,
        ),
    ]
