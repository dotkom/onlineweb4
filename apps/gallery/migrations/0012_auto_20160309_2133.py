# Generated by Django 1.9.4 on 2016-03-09 20:33

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("gallery", "0011_responsiveimage_photographer")]

    operations = [
        migrations.AlterField(
            model_name="responsiveimage",
            name="description",
            field=models.TextField(
                blank=True, default="", max_length=2048, verbose_name="Beskrivelse"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="image_lg",
            field=models.ImageField(
                upload_to="images/responsive", verbose_name="LG Bilde"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="image_md",
            field=models.ImageField(
                upload_to="images/responsive", verbose_name="MD Bilde"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="image_original",
            field=models.ImageField(
                upload_to="images/responsive", verbose_name="Originalbilde"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="image_sm",
            field=models.ImageField(
                upload_to="images/responsive", verbose_name="SM Bilde"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="image_wide",
            field=models.ImageField(
                upload_to="images/responsive/wide", verbose_name="Bredformat"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="image_xs",
            field=models.ImageField(
                upload_to="images/responsive", verbose_name="XS Bilde"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="photographer",
            field=models.CharField(
                blank=True, default="", max_length=100, verbose_name="Fotograf"
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="tags",
            field=taggit.managers.TaggableManager(
                help_text="En komma eller mellomrom-separert liste med tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AlterField(
            model_name="responsiveimage",
            name="thumbnail",
            field=models.ImageField(
                upload_to="images/responsive/thumbnails", verbose_name="Thumbnail"
            ),
        ),
        migrations.AlterField(
            model_name="unhandledimage",
            name="image",
            field=models.ImageField(upload_to="images/non-edited"),
        ),
        migrations.AlterField(
            model_name="unhandledimage",
            name="thumbnail",
            field=models.ImageField(upload_to="images/non-edited/thumbnails"),
        ),
    ]
