# Generated by Django 3.0.4 on 2020-03-30 07:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("authentication", "0045_auto_20200222_1436")]

    operations = [
        migrations.AddField(
            model_name="onlinegroup",
            name="application_description",
            field=models.TextField(
                blank=True,
                help_text="Beskriv gruppen for de som ønsker å søke under et opptak",
                max_length=2048,
                verbose_name="Opptaksbeskrivelse",
            ),
        ),
        migrations.AlterField(
            model_name="grouprole",
            name="role_type",
            field=models.CharField(
                choices=[
                    ("leader", "Leder"),
                    ("board_member", "Styremedlem"),
                    ("deputy_leader", "Nestleder"),
                    ("treasurer", "Økonomiansvarlig"),
                    ("chief_editor", "Redaktør"),
                ],
                max_length=256,
                unique=True,
                verbose_name="Rolle",
            ),
        ),
    ]
