# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0004_article_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.ForeignKey(default=None, blank=True, to='gallery.ResponsiveImage', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
