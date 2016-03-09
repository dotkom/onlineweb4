# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Approval',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='opprettet')),
                ('processed', models.BooleanField(default=False, verbose_name='behandlet', editable=False)),
                ('processed_date', models.DateTimeField(null=True, verbose_name='behandlet dato', blank=True)),
                ('approved', models.BooleanField(default=False, verbose_name='godkjent', editable=False)),
                ('message', models.TextField(verbose_name='melding')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MembershipApproval',
            fields=[
                ('approval_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='approval.Approval')),
                ('new_expiry_date', models.DateField(null=True, verbose_name='ny utl\xf8psdato', blank=True)),
                ('field_of_study', models.SmallIntegerField(default=0, verbose_name='studieretning', choices=[(0, 'Gjest'), (1, 'Bachelor i Informatikk (BIT)'), (10, 'Software (SW)'), (11, 'Informasjonsforvaltning (DIF)'), (12, 'Komplekse Datasystemer (KDS)'), (13, 'Spillteknologi (SPT)'), (14, 'Intelligente Systemer (IRS)'), (15, 'Helseinformatikk (MSMEDTEK)'), (30, 'Annen mastergrad'), (80, 'PhD'), (90, 'International'), (100, 'Annet Onlinemedlem')])),
                ('started_date', models.DateField(null=True, verbose_name='startet dato', blank=True)),
            ],
            options={
                'verbose_name': 'medlemskapss\xf8knad',
                'verbose_name_plural': 'medlemskapss\xf8knader',
                'permissions': (('view_membershipapproval', 'View membership approval'),),
            },
            bases=('approval.approval',),
        ),
    ]
