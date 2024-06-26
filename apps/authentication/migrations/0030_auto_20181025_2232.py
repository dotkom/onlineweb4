# Generated by Django 1.11.16 on 2018-10-25 20:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("authentication", "0029_auto_20180914_1305")]

    operations = [
        migrations.AlterField(
            model_name="onlineuser",
            name="ntnu_username",
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                unique=True,
                verbose_name="NTNU-brukernavn",
            ),
        )
    ]
