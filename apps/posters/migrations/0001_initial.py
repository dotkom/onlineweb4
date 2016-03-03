# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(max_length=50)),
                ('text', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderMixin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_type', models.IntegerField(choices=[(1, b'Plakat'), (2, b'Bong'), (3, b'Annet')])),
                ('ordered_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(max_length=1000, null=True, verbose_name='beskrivelse', blank=True)),
                ('amount', models.IntegerField(null=True, verbose_name='antall opplag', blank=True)),
                ('finished', models.BooleanField(default=False, verbose_name='ferdig')),
                ('display_from', models.DateField(default=None, null=True, verbose_name='vis fra', blank=True)),
            ],
            options={
                'permissions': (('add_poster_order', 'Add poster orders'), ('overview_poster_order', 'View poster order overview'), ('view_poster_order', 'View poster orders')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Poster',
            fields=[
                ('ordermixin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='posters.OrderMixin')),
                ('title', models.CharField(max_length=60, null=True, verbose_name='arrangementstittel', blank=True)),
                ('price', models.DecimalField(null=True, verbose_name='pris', max_digits=10, decimal_places=2, blank=True)),
                ('display_to', models.DateField(default=None, null=True, verbose_name='vis til', blank=True)),
                ('bong', models.IntegerField(null=True, verbose_name='bonger', blank=True)),
                ('event', models.ForeignKey(related_name='Arrangement', blank=True, to='events.Event', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'bestilling',
                'verbose_name_plural': 'bestillinger',
                'permissions': (('add_poster_order', 'Add poster orders'), ('overview_poster_order', 'View poster order overview'), ('view_poster_order', 'View poster orders')),
            },
            bases=('posters.ordermixin',),
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='assigned_to',
            field=models.ForeignKey(related_name='tilordnet til', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='ordered_by',
            field=models.ForeignKey(related_name='bestilt av', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='ordered_committee',
            field=models.ForeignKey(related_name='bestilt av komite', to='auth.Group'),
            preserve_default=True,
        ),
    ]
