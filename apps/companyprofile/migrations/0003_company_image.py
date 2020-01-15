# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0003_auto_20151015_0010"),
        ("companyprofile", "0002_auto_20151014_2132"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="image",
            field=models.ForeignKey(
                null=True,
                default=None,
                to="gallery.ResponsiveImage",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        )
    ]
