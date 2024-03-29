# Generated by Django 2.2.10 on 2020-03-05 13:03

from django.db import migrations


def load_data(apps, schema_editor):
    PaymentTransaction = apps.get_model("payment", "PaymentTransaction")

    for transaction in PaymentTransaction.objects.all():
        if transaction.used_stripe:
            transaction.source = "stripe"
        else:
            transaction.source = "cash"
        transaction.save(update_fields=["source"])


def remove_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("payment", "0031_paymenttransaction_source")]

    operations = [migrations.RunPython(load_data, remove_data)]
