# Generated by Django 3.2.23 on 2024-01-24 20:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0050_alter_onlineuser_first_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="onlineuser",
            name="cognito_subject",
            field=models.UUIDField(
                blank=True, null=True, verbose_name="Cognito User Id", unique=True
            ),
        ),
    ]