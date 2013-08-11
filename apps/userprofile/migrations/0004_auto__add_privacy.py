# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Privacy'
        db.create_table(u'userprofile_privacy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('expose_username', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_first_name', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_last_name', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_field_of_study', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_started_date', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_compiled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_phone_number', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('expose_address', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='privacy', unique=True, to=orm['auth.User'])),
        ))
        db.send_create_signal(u'userprofile', ['Privacy'])


    def backwards(self, orm):
        # Deleting model 'Privacy'
        db.delete_table(u'userprofile_privacy')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'userprofile.privacy': {
            'Meta': {'object_name': 'Privacy'},
            'expose_address': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_compiled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_field_of_study': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_first_name': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_last_name': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_phone_number': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_started_date': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expose_username': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'privacy'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'userprofile.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'allergies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'area_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'compiled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field_of_study': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'infomail': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mark_rules': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'rfid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'started_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 8, 11, 0, 0)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'userprofile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['userprofile']