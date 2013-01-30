# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Issue.release_date'
        db.alter_column('offline_issue', 'release_date', self.gf('django.db.models.fields.DateField')())


    def backwards(self, orm):
        
        # Changing field 'Issue.release_date'
        db.alter_column('offline_issue', 'release_date', self.gf('django.db.models.fields.DateTimeField')())


    models = {
        'offline.issue': {
            'Meta': {'ordering': "['-release_date']", 'object_name': 'Issue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('filebrowser.fields.FileBrowseField', [], {'max_length': '500', 'blank': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'thumb': ('filebrowser.fields.FileBrowseField', [], {'max_length': '500', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['offline']
