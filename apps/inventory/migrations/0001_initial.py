# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Item'
        db.create_table(u'inventory_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'inventory', ['Item'])

        # Adding model 'Batch'
        db.create_table(u'inventory_batch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='batches', to=orm['inventory.Item'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('expiration_date', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal(u'inventory', ['Batch'])


    def backwards(self, orm):
        # Deleting model 'Item'
        db.delete_table(u'inventory_item')

        # Deleting model 'Batch'
        db.delete_table(u'inventory_batch')


    models = {
        u'inventory.batch': {
            'Meta': {'object_name': 'Batch'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'batches'", 'to': u"orm['inventory.Item']"})
        },
        u'inventory.item': {
            'Meta': {'object_name': 'Item'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['inventory']