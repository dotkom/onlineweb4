# Generated by Django 2.1.9 on 2019-09-16 12:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payment", "0029_set_succeeded_relations_to_done")]

    operations = [
        migrations.AddField(
            model_name="paymenttransaction",
            name="stripe_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="paymentrelation",
            name="stripe_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
