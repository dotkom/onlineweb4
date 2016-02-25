# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0002_payment_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentDelay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valid_to', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
                ('payment', models.ForeignKey(to='payment.Payment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='description',
            new_name='multiple_description',
        ),
        migrations.AlterField(
            model_name='payment',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
