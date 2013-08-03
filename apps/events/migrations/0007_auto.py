# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing M2M table for field rules on 'AttendanceEvent'
        db.delete_table('events_attendanceevent_rules')


    def backwards(self, orm):
        # Adding M2M table for field rules on 'AttendanceEvent'
        db.create_table('events_attendanceevent_rules', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attendanceevent', models.ForeignKey(orm['events.attendanceevent'], null=False)),
            ('rule', models.ForeignKey(orm['events.rule'], null=False))
        ))
        db.create_unique('events_attendanceevent_rules', ['attendanceevent_id', 'rule_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'events.attendanceevent': {
            'Meta': {'object_name': 'AttendanceEvent'},
            'event': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'attendance_event'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['events.Event']"}),
            'max_capacity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'registration_end': ('django.db.models.fields.DateTimeField', [], {}),
            'registration_start': ('django.db.models.fields.DateTimeField', [], {}),
            'rule_bundles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['events.RuleBundle']", 'null': 'True', 'blank': 'True'})
        },
        'events.attendee': {
            'Meta': {'ordering': "['timestamp']", 'object_name': 'Attendee'},
            'attended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attendees'", 'to': "orm['events.AttendanceEvent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'events.companyevent': {
            'Meta': {'object_name': 'CompanyEvent'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['companyprofile.Company']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'oppretter'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'event_end': ('django.db.models.fields.DateTimeField', [], {}),
            'event_start': ('django.db.models.fields.DateTimeField', [], {}),
            'event_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingress': ('django.db.models.fields.TextField', [], {}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'events.fieldofstudyrule': {
            'Meta': {'object_name': 'FieldOfStudyRule', '_ormbases': ['events.Rule']},
            'field_of_study': ('django.db.models.fields.SmallIntegerField', [], {}),
            'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['events.Rule']", 'unique': 'True', 'primary_key': 'True'})
        },
        'events.graderule': {
            'Meta': {'object_name': 'GradeRule', '_ormbases': ['events.Rule']},
            'grade': ('django.db.models.fields.SmallIntegerField', [], {}),
            'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['events.Rule']", 'unique': 'True', 'primary_key': 'True'})
        },
        'events.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': "orm['events.RuleOffset']", 'null': 'True', 'blank': 'True'})
        },
        'events.rulebundle': {
            'Meta': {'object_name': 'RuleBundle'},
            'field_of_study_rules': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['events.FieldOfStudyRule']", 'null': 'True', 'blank': 'True'}),
            'grade_rules': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['events.GradeRule']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'events.ruleoffset': {
            'Meta': {'object_name': 'RuleOffset'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'events.usergrouprule': {
            'Meta': {'object_name': 'UserGroupRule', '_ormbases': ['events.Rule']},
            'rule_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['events.Rule']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['events']