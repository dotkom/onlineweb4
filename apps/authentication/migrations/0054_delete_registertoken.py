# Generated by Django 3.2.23 on 2024-02-01 15:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0053_yeet_cognito_for_auth0"),
    ]

    operations = [
        migrations.DeleteModel(
            name="RegisterToken",
        ),
    ]