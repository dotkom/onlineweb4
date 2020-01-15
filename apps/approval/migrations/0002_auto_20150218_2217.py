# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("approval", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="approval",
            name="applicant",
            field=models.ForeignKey(
                related_name="applicant",
                editable=False,
                to=settings.AUTH_USER_MODEL,
                verbose_name="s\xf8ker",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="approval",
            name="approver",
            field=models.ForeignKey(
                related_name="approver",
                blank=True,
                editable=False,
                to=settings.AUTH_USER_MODEL,
                null=True,
                verbose_name="godkjenner",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
