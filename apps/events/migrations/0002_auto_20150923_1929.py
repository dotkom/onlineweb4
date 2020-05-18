# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("events", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Extras",
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
                ("choice", models.CharField(max_length=69, verbose_name="valg")),
                (
                    "note",
                    models.CharField(
                        max_length=200, null=True, verbose_name="notat", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ["choice"],
                "verbose_name": "ekstra valg",
                "verbose_name_plural": "ekstra valg",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="attendanceevent",
            name="extras",
            field=models.ManyToManyField(to="events.Extras", null=True, blank=True),
            preserve_default=True,
        ),
    ]
