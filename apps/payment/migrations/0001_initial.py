# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('price', models.IntegerField(verbose_name='pris')),
                ('deadline', models.DateTimeField(null=True, verbose_name='frist', blank=True)),
                ('instant_payment', models.BooleanField(default=False, help_text='krev betaling f\xf8r p\xe5melding', verbose_name='betaling f\xf8r p\xe5melding')),
                ('description', models.CharField(help_text='Dette feltet kreves kun dersom det er mer enn en betaling', max_length=60, null=True, verbose_name='beskrivelse', blank=True)),
                ('added_date', models.DateTimeField(auto_now=True, verbose_name='opprettet dato')),
                ('changed_date', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('last_changed_by', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'betaling',
                'verbose_name_plural': 'betalinger',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PaymentRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('unique_id', models.CharField(max_length=128, null=True, blank=True)),
                ('payment', models.ForeignKey(to='payment.Payment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'betalingsrelasjon',
                'verbose_name_plural': 'betalingsrelasjoner',
            },
            bases=(models.Model,),
        ),
    ]
