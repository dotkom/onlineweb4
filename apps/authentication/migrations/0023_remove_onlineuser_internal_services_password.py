# Generated by Django 1.9.5 on 2016-04-27 20:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("authentication", "0022_onlineuser_internal_services_password")]

    operations = [
        migrations.RemoveField(
            model_name="onlineuser", name="internal_services_password"
        )
    ]
