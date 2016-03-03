# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResponsiveImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Navn')),
                ('date', models.DateField(auto_now_add=True)),
                ('image_original', models.FileField(upload_to=b'images/responsive', verbose_name='Originalbilde')),
                ('image_lg', models.ImageField(upload_to=b'images/responsive', verbose_name='LG Bilde')),
                ('image_md', models.ImageField(upload_to=b'images/responsive', verbose_name='MD Bilde')),
                ('image_sm', models.ImageField(upload_to=b'images/responsive', verbose_name='SM Bilde')),
                ('image_xs', models.ImageField(upload_to=b'images/responsive', verbose_name='XS Bilde')),
                ('thumbnail', models.ImageField(upload_to=b'images/responsive/thumbnails', verbose_name='Thumbnail')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnhandledImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'images/non-edited')),
                ('thumbnail', models.ImageField(upload_to=b'images/non-edited/thumbnails')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
