# Generated by Django 5.0.7 on 2024-07-28 20:52

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import apps.marks.models


class Migration(migrations.Migration):
    dependencies = [
        ("marks", "0011_remove_suspension_active_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="mark",
            name="category",
            field=models.SmallIntegerField(
                choices=[
                    (0, "Ingen"),
                    (1, "Sosialt"),
                    (2, "Bedriftspresentasjon"),
                    (3, "Kurs"),
                    (4, "Tilbakemelding"),
                    (5, "Kontoret"),
                    (6, "Betaling"),
                ],
                default=0,
                editable=False,
                verbose_name="kategori",
            ),
        ),
        migrations.AlterField(
            model_name="mark",
            name="cause",
            field=models.CharField(
                choices=[
                    ("sen avmelding", "Avmelding etter avmeldingsfrist"),
                    (
                        "veldig sen avmelding",
                        "Avmelding under 2 timer før arrangementstart",
                    ),
                    (
                        "sent oppmøte",
                        "Oppmøte etter arrangementets start eller innslipp er ferdig",
                    ),
                    ("manglende oppmøte", "Manglende oppmøte"),
                    (
                        "manglende tilbakemelding",
                        "Svarte ikke på tilbakemeldingsskjema",
                    ),
                    ("manglende betaling", "Manglende betaling"),
                    ("annet", "Annet"),
                ],
                default="annet",
                max_length=30,
                verbose_name="årsak",
            ),
        ),
        migrations.AlterField(
            model_name="mark",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Settes automatisk basert på årsak.",
                max_length=255,
                verbose_name="beskrivelse",
            ),
        ),
        migrations.AlterField(
            model_name="mark",
            name="ruleset",
            field=models.ForeignKey(
                default=apps.marks.models.MarkRuleSet.get_current_rule_set_pk,
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="marks.markruleset",
                verbose_name="Gjeldene prikkregler",
            ),
        ),
        migrations.AlterField(
            model_name="mark",
            name="weight",
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text="Settes automatisk basert på årsak. Se prikkreglene for veiledning",
                verbose_name="Vekting",
            ),
        ),
        migrations.AlterField(
            model_name="markuser",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="suspension",
            name="created_time",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="Utdelt tidspunkt",
            ),
        ),
        migrations.AlterField(
            model_name="suspension",
            name="user",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
