# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Company'
        db.create_table(u'companyprofile_company', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_description', self.gf('django.db.models.fields.TextField')(max_length=200)),
            ('long_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.IntegerField')(max_length=8, null=True, blank=True)),
        ))
        db.send_create_signal(u'companyprofile', ['Company'])


    def backwards(self, orm):
        # Deleting model 'Company'
        db.delete_table(u'companyprofile_company')


    models = {
        u'companyprofile.company': {
            'Meta': {'object_name': 'Company'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['companyprofile']