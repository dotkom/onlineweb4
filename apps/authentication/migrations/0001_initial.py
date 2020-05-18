# -*- coding: utf-8 -*-


import datetime

import django.core.validators
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("auth", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="OnlineUser",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        unique=True,
                        max_length=30,
                        verbose_name="username",
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[\\w.@+-]+$", "Enter a valid username.", "invalid"
                            )
                        ],
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        max_length=30, verbose_name="first name", blank=True
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        max_length=30, verbose_name="last name", blank=True
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=75, verbose_name="email address", blank=True
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "field_of_study",
                    models.SmallIntegerField(
                        default=0,
                        verbose_name="studieretning",
                        choices=[
                            (0, "Gjest"),
                            (1, "Bachelor i Informatikk (BIT)"),
                            (10, "Software (SW)"),
                            (11, "Informasjonsforvaltning (DIF)"),
                            (12, "Komplekse Datasystemer (KDS)"),
                            (13, "Spillteknologi (SPT)"),
                            (14, "Intelligente Systemer (IRS)"),
                            (15, "Helseinformatikk (MSMEDTEK)"),
                            (30, "Annen mastergrad"),
                            (80, "PhD"),
                            (90, "International"),
                            (100, "Annet Onlinemedlem"),
                        ],
                    ),
                ),
                (
                    "started_date",
                    models.DateField(
                        default=datetime.date(2015, 2, 18),
                        verbose_name="startet studie",
                    ),
                ),
                (
                    "compiled",
                    models.BooleanField(default=False, verbose_name="kompilert"),
                ),
                (
                    "infomail",
                    models.BooleanField(default=False, verbose_name="vil ha infomail"),
                ),
                (
                    "phone_number",
                    models.CharField(
                        max_length=20,
                        null=True,
                        verbose_name="telefonnummer",
                        blank=True,
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        max_length=100, null=True, verbose_name="adresse", blank=True
                    ),
                ),
                (
                    "zip_code",
                    models.CharField(
                        max_length=4, null=True, verbose_name="postnummer", blank=True
                    ),
                ),
                (
                    "allergies",
                    models.TextField(null=True, verbose_name="allergier", blank=True),
                ),
                (
                    "mark_rules",
                    models.BooleanField(
                        default=False, verbose_name="godtatt prikkeregler"
                    ),
                ),
                (
                    "rfid",
                    models.CharField(
                        max_length=50, null=True, verbose_name="RFID", blank=True
                    ),
                ),
                (
                    "nickname",
                    models.CharField(
                        max_length=50, null=True, verbose_name="nickname", blank=True
                    ),
                ),
                (
                    "website",
                    models.URLField(null=True, verbose_name="hjemmeside", blank=True),
                ),
                (
                    "gender",
                    models.CharField(
                        default=b"male",
                        max_length=10,
                        verbose_name="kj\xf8nn",
                        choices=[(b"male", "mann"), (b"female", "kvinne")],
                    ),
                ),
                (
                    "ntnu_username",
                    models.CharField(
                        max_length=10,
                        unique=True,
                        null=True,
                        verbose_name="NTNU-brukernavn",
                        blank=True,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Group",
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of his/her group.",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Permission",
                        blank=True,
                        help_text="Specific permissions for this user.",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ["first_name", "last_name"],
                "verbose_name": "brukerprofil",
                "verbose_name_plural": "brukerprofiler",
                "permissions": (("view_onlineuser", "View OnlineUser"),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AllowedUsername",
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
                    "username",
                    models.CharField(
                        unique=True, max_length=10, verbose_name="NTNU-brukernavn"
                    ),
                ),
                ("registered", models.DateField(verbose_name="registrert")),
                ("note", models.CharField(max_length=100, verbose_name="notat")),
                (
                    "description",
                    models.TextField(null=True, verbose_name="beskrivelse", blank=True),
                ),
                ("expiration_date", models.DateField(verbose_name="utl\xf8psdato")),
            ],
            options={
                "ordering": ("username",),
                "verbose_name": "medlem",
                "verbose_name_plural": "medlemsregister",
                "permissions": (("view_allowedusername", "View AllowedUsername"),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Email",
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
                    "email",
                    models.EmailField(
                        unique=True, max_length=75, verbose_name="epostadresse"
                    ),
                ),
                (
                    "primary",
                    models.BooleanField(default=False, verbose_name="prim\xe6r"),
                ),
                (
                    "verified",
                    models.BooleanField(
                        default=False, verbose_name="verifisert", editable=False
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="email_user",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "epostadresse",
                "verbose_name_plural": "epostadresser",
                "permissions": (("view_email", "View Email"),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Position",
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
                    "period",
                    models.CharField(
                        default=b"2013-2014", max_length=9, verbose_name="periode"
                    ),
                ),
                (
                    "committee",
                    models.CharField(
                        default=b"hs",
                        max_length=10,
                        verbose_name="komite",
                        choices=[
                            (b"hs", "Hovedstyret"),
                            (b"appkom", "Applikasjonskomiteen"),
                            (b"arrkom", "Arrangementskomiteen"),
                            (b"bankom", "Bank- og \xf8konomikomiteen"),
                            (b"bedkom", "Bedriftskomiteen"),
                            (b"dotkom", "Drifts- og utviklingskomiteen"),
                            (b"ekskom", "Ekskursjonskomiteen"),
                            (b"fagkom", "Fag- og kurskomiteen"),
                            (b"jubkom", "Jubileumskomiteen"),
                            (b"pangkom", "Pensjonistkomiteen"),
                            (b"prokom", "Profil-og aviskomiteen"),
                            (b"trikom", "Trivselskomiteen"),
                            (b"velkom", "Velkomstkomiteen"),
                        ],
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        default=b"medlem",
                        max_length=10,
                        verbose_name="stilling",
                        choices=[
                            (b"medlem", "Medlem"),
                            (b"leder", "Leder"),
                            (b"nestleder", "Nestleder"),
                            (b"okoans", "\xd8konomiansvarlig"),
                        ],
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="positions",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("user", "period"),
                "verbose_name": "posisjon",
                "verbose_name_plural": "posisjoner",
                "permissions": (("view_position", "View Position"),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="RegisterToken",
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
                ("email", models.EmailField(max_length=254, verbose_name="epost")),
                ("token", models.CharField(max_length=32, verbose_name="token")),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="opprettet dato"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="register_user",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"permissions": (("view_registertoken", "View RegisterToken"),)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SpecialPosition",
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
                ("position", models.CharField(max_length=50, verbose_name="Posisjon")),
                (
                    "since_year",
                    models.IntegerField(max_length=4, verbose_name="Medlem siden"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="special_positions",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("user", "since_year"),
                "verbose_name": "spesialposisjon",
                "verbose_name_plural": "spesialposisjoner",
                "permissions": (("view_specialposition", "View SpecialPosition"),),
            },
            bases=(models.Model,),
        ),
    ]
