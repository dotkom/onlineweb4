# Generated by Django 5.0.7 on 2024-07-29 21:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("marks", "0012_alter_mark_category_alter_mark_cause_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mark",
            name="expiration_date",
            field=models.DateField(
                help_text="Settes automatisk", verbose_name="Utløpsdato"
            ),
        ),
    ]
