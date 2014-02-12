# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Company.site'
        db.alter_column(u'companyprofile_company', 'site', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'Company.site'
        db.alter_column(u'companyprofile_company', 'site', self.gf('django.db.models.fields.URLField')(max_length=200))

    models = {
        u'companyprofile.company': {
            'Meta': {'object_name': 'Company'},
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '200'}),
            'long_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['companyprofile']