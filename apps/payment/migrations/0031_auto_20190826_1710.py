# Generated by Django 2.1.9 on 2019-08-26 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0030_auto_20190826_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fikenorderline',
            name='sale',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_lines', to='payment.FikenSale'),
        ),
    ]