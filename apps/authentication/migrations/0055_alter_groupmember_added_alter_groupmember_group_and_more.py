# Generated by Django 5.0.3 on 2024-03-25 15:26

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0054_delete_registertoken"),
    ]

    operations = [
        migrations.AlterField(
            model_name="groupmember",
            name="added",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AlterField(
            model_name="groupmember",
            name="group",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="members",
                to="authentication.onlinegroup",
                verbose_name="Onlinegruppe",
            ),
        ),
        migrations.AlterField(
            model_name="groupmember",
            name="user",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="group_memberships",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Bruker",
            ),
        ),
    ]