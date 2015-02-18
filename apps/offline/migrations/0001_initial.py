# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Issue'
        db.create_table('offline_issue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('release_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('thumb', self.gf('filebrowser.fields.FileBrowseField')(max_length=500, blank=True)),
            ('issue', self.gf('filebrowser.fields.FileBrowseField')(max_length=500, blank=True)),
        ))
        db.send_create_signal('offline', ['Issue'])


    def backwards(self, orm):
        
        # Deleting model 'Issue'
        db.delete_table('offline_issue')


    models = {
        'offline.issue': {
            'Meta': {'object_name': 'Issue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('filebrowser.fields.FileBrowseField', [], {'max_length': '500', 'blank': 'True'}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {}),
            'thumb': ('filebrowser.fields.FileBrowseField', [], {'max_length': '500', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['offline']
