import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("approval", "0012_auto_20200330_0903")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE approval_committeeapplicationperiod_committees RENAME TO "
                    "approval_committeeapplicationperiodparticipation",
                    reverse_sql="ALTER TABLE approval_committeeapplicationperiodparticipation RENAME TO "
                    "approval_committeeapplicationperiod_committees",
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="CommitteeApplicationPeriodParticipation",
                    fields=[
                        (
                            "id",
                            models.AutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "committeeapplicationperiod",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                to="approval.CommitteeApplicationPeriod",
                            ),
                        ),
                        (
                            "onlinegroup",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                to="authentication.OnlineGroup",
                            ),
                        ),
                    ],
                ),
                migrations.AlterField(
                    model_name="committeeapplicationperiod",
                    name="committees",
                    field=models.ManyToManyField(
                        to="authentication.OnlineGroup",
                        through="approval.CommitteeApplicationPeriodParticipation",
                        related_name="application_periods",
                        verbose_name="Komiteer",
                        # help_text isn't saved in the DB, so changing it here is OK
                        help_text="Komiteer som deltar i opptaken, men ikke nødvendigvis kan søkes opptak til",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="committeeapplicationperiodparticipation",
            name="open_for_applications",
            field=models.BooleanField(verbose_name="Åpen for søknader", default=True),
        ),
        migrations.AlterModelOptions(
            name="committeeapplicationperiodparticipation",
            options={
                "ordering": ("pk",),
                "verbose_name": "Komité i opptaksperiode",
                "verbose_name_plural": "Komité i opptaksperioder",
            },
        ),
        migrations.AlterField(
            model_name="committeeapplicationperiod",
            name="deadline",
            field=models.DateTimeField(verbose_name="Frist"),
        ),
    ]
