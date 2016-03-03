# -*- coding: utf-8 -*-


from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='tittel')),
                ('release_date', models.DateField(verbose_name='utgivelsesdato')),
                ('description', models.TextField(null=True, verbose_name='beskrivelse', blank=True)),
                ('issue', filebrowser.fields.FileBrowseField(max_length=500, verbose_name='pdf')),
            ],
            options={
                'ordering': ['-release_date'],
                'verbose_name': 'Utgivelse',
                'verbose_name_plural': 'Utgivelser',
                'permissions': (('view_issue', 'View Issue'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProxyChunk',
            fields=[
            ],
            options={
                'verbose_name': 'Informasjonstekst',
                'proxy': True,
                'verbose_name_plural': 'Informasjonstekster',
            },
            bases=('chunks.chunk',),
        ),
    ]
