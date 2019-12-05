# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("careeropportunity", "0002_auto_20151017_0250")]

    operations = [
        migrations.AlterModelOptions(
            name="careeropportunity",
            options={
                "verbose_name": "karrieremulighet",
                "verbose_name_plural": "karrieremuligheter",
                "permissions": (("view_careeropportunity", "View CareerOpportunity"),),
            },
        )
    ]
