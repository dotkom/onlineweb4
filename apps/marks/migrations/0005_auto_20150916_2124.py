# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marks', '0004_auto_20150916_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='suspension',
            name='payment_id',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='suspension',
            name='expiration_date',
            field=models.DateField(null=True, verbose_name='utl\xf8psdato', blank=True),
            preserve_default=True,
        ),
    ]
