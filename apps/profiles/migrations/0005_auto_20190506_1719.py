# Generated by Django 2.0.13 on 2019-05-06 15:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("profiles", "0004_auto_20180221_2241")]

    operations = [
        migrations.AlterModelOptions(
            name="privacy",
            options={
                "default_permissions": ("add", "change", "delete"),
                "permissions": (("view_privacy", "View Privacy"),),
                "verbose_name": "personvern",
                "verbose_name_plural": "personvern",
            },
        )
    ]
