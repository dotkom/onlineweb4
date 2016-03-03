# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_auto_20151015_0010'),
        ('companyprofile', '0002_auto_20151014_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='image',
            field=models.ForeignKey(null=True, default=None, to='gallery.ResponsiveImage'),
            preserve_default=True,
        ),
    ]
