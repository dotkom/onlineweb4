# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Offline'
        db.create_table('offline_offline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('intro_text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('offline', ['Offline'])


    def backwards(self, orm):
        
        # Deleting model 'Offline'
        db.delete_table('offline_offline')


    models = {
        'offline.issue': {
            'Meta': {'ordering': "['-release_date']", 'object_name': 'Issue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('filebrowser.fields.FileBrowseField', [], {'max_length': '500', 'blank': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'offline.offline': {
            'Meta': {'object_name': 'Offline'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['offline']
