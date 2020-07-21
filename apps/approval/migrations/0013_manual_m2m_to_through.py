from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("approval", "0012_auto_20200330_0903")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE approval_committeeapplicationperiod_committees RENAME TO "
                    "approval_commiteeapplicationperiodparticipation",
                    reverse_sql="ALTER TABLE approval_commiteeapplicationperiodparticipation RENAME TO "
                    "approval_committeeapplicationperiod_committees",
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="CommiteeApplicationPeriodParticipation",
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
                        through="approval.CommiteeApplicationPeriodParticipation",
                        related_name="application_periods",
                        verbose_name="Komiteer",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="commiteeapplicationperiodparticipation",
            name="open_for_applications",
            field=models.BooleanField(verbose_name="Åpen for søknader", default=True),
        ),
    ]
