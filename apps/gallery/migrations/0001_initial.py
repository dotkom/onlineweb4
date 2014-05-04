# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UnhandledImage'
        db.create_table(u'gallery_unhandledimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'gallery', ['UnhandledImage'])

        # Adding model 'ResponsiveImage'
        db.create_table(u'gallery_responsiveimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image_original', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('image_lg', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('image_md', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('image_sm', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('image_xs', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'gallery', ['ResponsiveImage'])


    def backwards(self, orm):
        # Deleting model 'UnhandledImage'
        db.delete_table(u'gallery_unhandledimage')

        # Deleting model 'ResponsiveImage'
        db.delete_table(u'gallery_responsiveimage')


    models = {
        u'gallery.responsiveimage': {
            'Meta': {'object_name': 'ResponsiveImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_lg': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'image_md': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'image_original': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'image_sm': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'image_xs': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        u'gallery.unhandledimage': {
            'Meta': {'object_name': 'UnhandledImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['gallery']