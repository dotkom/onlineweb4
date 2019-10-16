# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0004_responsiveimage_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsiveimage',
            name='image_wide',
            field=models.FileField(default='', upload_to=b'images/responsive/wide', verbose_name='Bredformat'),
            preserve_default=False,
        ),
    ]
