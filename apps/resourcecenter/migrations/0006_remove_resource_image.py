# Generated by Django 2.1.8 on 2019-05-10 21:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("resourcecenter", "0005_merge_20190510_2322")]

    operations = [migrations.RemoveField(model_name="resource", name="image")]
