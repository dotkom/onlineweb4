# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OnlineUser'
        db.create_table(u'authentication_onlineuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=254)),
            ('field_of_study', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('started_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 8, 0, 0))),
            ('compiled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('infomail', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('area_code', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('allergies', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mark_rules', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rfid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'authentication', ['OnlineUser'])

        # Adding model 'RegisterToken'
        db.create_table(u'authentication_registertoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.OnlineUser'])),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 6, 8, 0, 0), auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'authentication', ['RegisterToken'])


    def backwards(self, orm):
        # Deleting model 'OnlineUser'
        db.delete_table(u'authentication_onlineuser')

        # Deleting model 'RegisterToken'
        db.delete_table(u'authentication_registertoken')


    models = {
        u'authentication.onlineuser': {
            'Meta': {'object_name': 'OnlineUser'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'allergies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'area_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'compiled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254'}),
            'field_of_study': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infomail': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'mark_rules': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'rfid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'started_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 8, 0, 0)'})
        },
        u'authentication.registertoken': {
            'Meta': {'object_name': 'RegisterToken'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 8, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authentication.OnlineUser']"})
        }
    }

    complete_apps = ['authentication']