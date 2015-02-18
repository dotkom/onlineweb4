# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Issue.thumb'
        db.delete_column('offline_issue', 'thumb')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Issue.thumb'
        raise RuntimeError("Cannot reverse this migration. 'Issue.thumb' and its values cannot be restored.")


    models = {
        'offline.issue': {
            'Meta': {'ordering': "['-release_date']", 'object_name': 'Issue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('filebrowser.fields.FileBrowseField', [], {'max_length': '500', 'blank': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['offline']
