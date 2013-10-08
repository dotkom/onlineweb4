# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Event.ingress_short'
        db.add_column(u'events_event', 'ingress_short',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150),
                      keep_default=False)


        # Changing field 'Event.title'
        db.alter_column(u'events_event', 'title', self.gf('django.db.models.fields.CharField')(max_length=45))

    def backwards(self, orm):
        # Deleting field 'Event.ingress_short'
        db.delete_column(u'events_event', 'ingress_short')


        # Changing field 'Event.title'
        db.alter_column(u'events_event', 'title', self.gf('django.db.models.fields.CharField')(max_length=100))

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
        u'authentication.onlineuser': {
            'Meta': {'object_name': 'OnlineUser'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'allergies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'compiled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'field_of_study': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infomail': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mark_rules': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ntnu_username': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'rfid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'started_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 9, 11, 0, 0)'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
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
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'events.attendanceevent': {
            'Meta': {'object_name': 'AttendanceEvent'},
            'event': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'attendance_event'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['events.Event']"}),
            'max_capacity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'registration_end': ('django.db.models.fields.DateTimeField', [], {}),
            'registration_start': ('django.db.models.fields.DateTimeField', [], {}),
            'rule_bundles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['events.RuleBundle']", 'null': 'True', 'blank': 'True'}),
            'waitlist': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'events.attendee': {
            'Meta': {'ordering': "['timestamp']", 'object_name': 'Attendee'},
            'attended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendees'", 'to': u"orm['events.AttendanceEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authentication.OnlineUser']"})
        },
        u'events.companyevent': {
            'Meta': {'object_name': 'CompanyEvent'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['companyprofile.Company']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'companies'", 'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'events.event': {
            'Meta': {'object_name': 'Event'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'oppretter'", 'to': u"orm['authentication.OnlineUser']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'event_end': ('django.db.models.fields.DateTimeField', [], {}),
            'event_start': ('django.db.models.fields.DateTimeField', [], {}),
            'event_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('filebrowser.fields.FileBrowseField', [], {'max_length': '200'}),
            'ingress': ('django.db.models.fields.TextField', [], {}),
            'ingress_short': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'events.fieldofstudyrule': {
            'Meta': {'object_name': 'FieldOfStudyRule', '_ormbases': [u'events.Rule']},
            'field_of_study': ('django.db.models.fields.SmallIntegerField', [], {}),
            u'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['events.Rule']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'events.graderule': {
            'Meta': {'object_name': 'GradeRule', '_ormbases': [u'events.Rule']},
            'grade': ('django.db.models.fields.SmallIntegerField', [], {}),
            u'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['events.Rule']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'events.rule': {
            'Meta': {'object_name': 'Rule'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['events.RuleOffset']", 'null': 'True', 'blank': 'True'})
        },
        u'events.rulebundle': {
            'Meta': {'object_name': 'RuleBundle'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'field_of_study_rules': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['events.FieldOfStudyRule']", 'null': 'True', 'blank': 'True'}),
            'grade_rules': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['events.GradeRule']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_group_rules': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['events.UserGroupRule']", 'null': 'True', 'blank': 'True'})
        },
        u'events.ruleoffset': {
            'Meta': {'object_name': 'RuleOffset'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        u'events.usergrouprule': {
            'Meta': {'object_name': 'UserGroupRule', '_ormbases': [u'events.Rule']},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['events.Rule']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['events']
