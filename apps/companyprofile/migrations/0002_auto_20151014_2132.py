# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companyprofile', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='image',
            new_name='old_image',
        ),
    ]
