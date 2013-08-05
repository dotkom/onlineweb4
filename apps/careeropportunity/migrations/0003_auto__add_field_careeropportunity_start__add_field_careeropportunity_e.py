# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CareerOpportunity.start'
        db.add_column(u'careeropportunity_careeropportunity', 'start',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 5, 0, 0)),
                      keep_default=False)

        # Adding field 'CareerOpportunity.end'
        db.add_column(u'careeropportunity_careeropportunity', 'end',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 5, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CareerOpportunity.start'
        db.delete_column(u'careeropportunity_careeropportunity', 'start')

        # Deleting field 'CareerOpportunity.end'
        db.delete_column(u'careeropportunity_careeropportunity', 'end')


    models = {
        u'careeropportunity.careeropportunity': {
            'Meta': {'object_name': 'CareerOpportunity'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'company'", 'to': u"orm['companyprofile.Company']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingress': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'companyprofile.company': {
            'Meta': {'object_name': 'Company'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '200'}),
            'long_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['careeropportunity']