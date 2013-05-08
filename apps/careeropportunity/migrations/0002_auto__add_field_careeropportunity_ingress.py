# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CareerOpportunity.ingress'
        db.add_column('careeropportunity_careeropportunity', 'ingress',
                      self.gf('django.db.models.fields.CharField')(default='test', max_length=250),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CareerOpportunity.ingress'
        db.delete_column('careeropportunity_careeropportunity', 'ingress')


    models = {
        'careeropportunity.careeropportunity': {
            'Meta': {'object_name': 'CareerOpportunity'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'company'", 'to': "orm['companyprofile.Company']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingress': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'companyprofile.company': {
            'Meta': {'object_name': 'Company'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['careeropportunity']