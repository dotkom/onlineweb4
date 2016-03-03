# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0007_auto_20151024_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsiveimage',
            name='image_original',
            field=models.ImageField(upload_to=b'images/responsive', verbose_name='Originalbilde'),
            preserve_default=True,
        ),
    ]
