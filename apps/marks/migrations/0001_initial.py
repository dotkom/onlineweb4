# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Mark",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=155, verbose_name="tittel")),
                ("added_date", models.DateField(verbose_name="utdelt dato")),
                (
                    "last_changed_date",
                    models.DateTimeField(auto_now=True, verbose_name="sist redigert"),
                ),
                (
                    "description",
                    models.CharField(
                        help_text="Hvis dette feltet etterlates blankt vil det fylles med en standard grunn for typen prikk som er valgt.",
                        max_length=255,
                        verbose_name="beskrivelse",
                        blank=True,
                    ),
                ),
                (
                    "category",
                    models.SmallIntegerField(
                        default=0,
                        verbose_name="kategori",
                        choices=[
                            (0, "Ingen"),
                            (1, "Sosialt"),
                            (2, "Bedriftspresentasjon"),
                            (3, "Kurs"),
                            (4, "Tilbakemelding"),
                            (5, "Kontoret"),
                        ],
                    ),
                ),
                (
                    "given_by",
                    models.ForeignKey(
                        related_name="mark_given_by",
                        blank=True,
                        editable=False,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        verbose_name="gitt av",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "last_changed_by",
                    models.ForeignKey(
                        related_name="marks_last_changed_by",
                        editable=False,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        verbose_name="sist redigert av",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "Prikk",
                "verbose_name_plural": "Prikker",
                "permissions": (("view_mark", "View Mark"),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MarkUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "expiration_date",
                    models.DateField(verbose_name="utl\xf8psdato", editable=False),
                ),
                (
                    "mark",
                    models.ForeignKey(
                        related_name="given_to",
                        to="marks.Mark",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("expiration_date",),
                "permissions": (("view_userentry", "View UserEntry"),),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="markuser", unique_together=set([("user", "mark")])
        ),
    ]
