# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_auto_20150916_1953'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='responsiveimage',
            options={'verbose_name': 'Responsivt Bilde', 'verbose_name_plural': 'Responsive Bilder', 'permissions': (('view_responsiveimage', 'View ResponsiveImage'),)},
        ),
    ]
