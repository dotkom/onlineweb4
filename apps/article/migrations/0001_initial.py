# -*- coding: utf-8 -*-


from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('heading', models.CharField(max_length=45, verbose_name='tittel')),
                ('ingress_short', models.CharField(max_length=100, verbose_name='kort ingress')),
                ('ingress', models.TextField(verbose_name='ingress')),
                ('content', models.TextField(verbose_name='content')),
                ('image', filebrowser.fields.FileBrowseField(max_length=200, null=True, verbose_name='bilde')),
                ('video', models.CharField(max_length=200, verbose_name='vimeo id', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='opprettet-dato')),
                ('changed_date', models.DateTimeField(auto_now=True, verbose_name='sist endret')),
                ('published_date', models.DateTimeField(verbose_name='publisert')),
                ('additional_authors', models.CharField(max_length=200, verbose_name='andre forfattere', blank=True)),
                ('photographers', models.CharField(max_length=200, verbose_name='fotograf(er)', blank=True)),
                ('featured', models.BooleanField(default=False, verbose_name='featured artikkel')),
            ],
            options={
                'ordering': ['published_date'],
                'verbose_name': 'artikkel',
                'verbose_name_plural': 'artikler',
                'permissions': (('view_article', 'View Article'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('article', models.ForeignKey(related_name='article_tags', verbose_name='artikkel', to='article.Article')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'permissions': (('view_articletag', 'View ArticleTag'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='navn')),
                ('slug', models.CharField(max_length=30, verbose_name='kort navn')),
            ],
            options={
                'permissions': (('view_tag', 'View Tag'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='articletag',
            name='tag',
            field=models.ForeignKey(related_name='article_tags', verbose_name='tag', to='article.Tag'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='articletag',
            unique_together=set([('article', 'tag')]),
        ),
    ]
