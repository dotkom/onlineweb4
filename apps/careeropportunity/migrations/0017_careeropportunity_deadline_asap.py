# Generated by Django 3.0.10 on 2021-03-21 21:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("careeropportunity", "0016_careeropportunity_application_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="careeropportunity",
            name="deadline_asap",
            field=models.BooleanField(
                blank=True, default=False, verbose_name="snarest"
            ),
        ),
    ]
