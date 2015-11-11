# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    replaces = [(b'webshop', '0001_initial'), (b'webshop', '0002_auto_20150325_2219'), (b'webshop', '0003_auto_20150422_1940'), (b'webshop', '0004_auto_20150901_2338'), (b'webshop', '0005_auto_20151007_2142'), (b'webshop', '0006_auto_20151104_2228'), (b'webshop', '0007_auto_20151104_2240'), (b'webshop', '0008_auto_20151104_2244'), (b'webshop', '0009_auto_20151104_2302'), (b'webshop', '0006_auto_20151104_2009'), (b'webshop', '0007_auto_20151104_2135'), (b'webshop', '0010_merge'), (b'webshop', '0011_product_deadline'), (b'webshop', '0012_product_active')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gallery', '0011_responsiveimage_photographer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('number', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('paid', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('short', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('stock', models.PositiveSmallIntegerField()),
                ('category', models.ForeignKey(to='webshop.Category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'')),
                ('product', models.ForeignKey(to='webshop.Product')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='order_line',
            field=models.ForeignKey(to='webshop.OrderLine'),
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(to='webshop.Product'),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Kategori', 'verbose_name_plural': 'Kategorier'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Bestilling', 'verbose_name_plural': 'Bestillinger'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Produkt', 'verbose_name_plural': 'Produkter'},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'verbose_name': 'Produktbilde', 'verbose_name_plural': 'Produktbilder'},
        ),
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='order_line',
            field=models.ForeignKey(related_name='orders', to='webshop.OrderLine'),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(related_name='products', to='webshop.Category'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(upload_to=b'images/webshop'),
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='product',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='number',
            new_name='quantity',
        ),
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.DecimalField(max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.CharField(max_length=25, verbose_name='St\xf8relse')),
                ('description', models.CharField(max_length=50, null=True, verbose_name='Beskrivelse', blank=True)),
                ('product', models.ForeignKey(default=1, to='webshop.Product')),
                ('stock', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='productsize',
            options={'verbose_name': 'St\xf8rrelse', 'verbose_name_plural': 'St\xf8rrelser'},
        ),
        migrations.AddField(
            model_name='order',
            name='size',
            field=models.ForeignKey(to='webshop.ProductSize', null=True),
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
        migrations.AddField(
            model_name='product',
            name='images_csv',
            field=models.CommaSeparatedIntegerField(default=None, max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='deadline',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
