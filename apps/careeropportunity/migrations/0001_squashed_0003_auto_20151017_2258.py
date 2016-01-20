# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [('careeropportunity', '0001_initial'), ('careeropportunity', '0002_auto_20151017_0250'), ('careeropportunity', '0003_auto_20151017_2258')]

    dependencies = [
        ('companyprofile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CareerOpportunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='tittel')),
                ('ingress', models.CharField(max_length=250, verbose_name='ingress')),
                ('description', models.TextField(verbose_name='beskrivelse')),
                ('start', models.DateTimeField(verbose_name='aktiv fra')),
                ('end', models.DateTimeField(verbose_name='aktiv til')),
                ('featured', models.BooleanField(default=False, verbose_name='fremhevet')),
                ('company', models.ForeignKey(related_name='company', to='companyprofile.Company')),
            ],
            options={
                'verbose_name': 'karrieremulighet',
                'verbose_name_plural': 'karrieremuligheter',
                'permissions': (('view_careeropportunity', 'View CareerOpportunity'),),
            },
            bases=(models.Model,),
        ),
    ]
