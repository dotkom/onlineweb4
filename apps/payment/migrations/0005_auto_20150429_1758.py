# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20150415_2210'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.IntegerField(verbose_name='pris')),
                ('description', models.CharField(max_length=128, null=True, blank=True)),
                ('payment', models.ForeignKey(to='payment.Payment')),
            ],
            options={
                'verbose_name': 'pris',
                'verbose_name_plural': 'priser',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='paymentdelay',
            options={'verbose_name': 'betalingsutsettelse', 'verbose_name_plural': 'betalingsutsettelser'},
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_key_index',
            field=models.SmallIntegerField(default=0, verbose_name='stripe key', choices=[(0, b'Arrkom'), (1, b'Prokom')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentrelation',
            name='payment_price',
            field=models.ForeignKey(default=0, to='payment.PaymentPrice'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentrelation',
            name='refunded',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='paymentrelation',
            name='stripe_id',
            field=models.CharField(default=0, max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='delay',
            field=models.SmallIntegerField(default=2, null=True, verbose_name='utsettelse', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='payment',
            unique_together=set([('content_type', 'object_id')]),
        ),
        migrations.RemoveField(
            model_name='payment',
            name='price',
        ),
        migrations.AlterUniqueTogether(
            name='paymentdelay',
            unique_together=set([('payment', 'user')]),
        ),
    ]
