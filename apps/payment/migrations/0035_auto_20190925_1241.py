# Generated by Django 2.1.11 on 2019-09-25 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0034_auto_20190925_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fikensaleattachment',
            name='attach_to_payment',
            field=models.BooleanField(default=False),
        ),
    ]