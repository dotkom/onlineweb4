# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FeedbackRelation.penalty'
        db.add_column('feedback_feedbackrelation', 'penalty',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'FeedbackRelation.penalty'
        db.delete_column('feedback_feedbackrelation', 'penalty')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'feedback_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'feedback.feedbackrelation': {
            'Meta': {'unique_together': "(('feedback', 'content_type', 'object_id'),)", 'object_name': 'FeedbackRelation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'answered': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'feedbacks'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'deadline': ('django.db.models.fields.DateField', [], {}),
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['feedback.Feedback']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'penalty': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'feedback.fieldofstudyanswer': {
            'Meta': {'object_name': 'FieldOfStudyAnswer'},
            'answer': ('django.db.models.fields.SmallIntegerField', [], {}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field_of_study_answers'", 'to': "orm['feedback.FeedbackRelation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': "orm['feedback.FieldOfStudyQuestion']"})
        },
        'feedback.fieldofstudyquestion': {
            'Meta': {'object_name': 'FieldOfStudyQuestion'},
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field_of_study_questions'", 'to': "orm['feedback.Feedback']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
        },
        'feedback.ratinganswer': {
            'Meta': {'object_name': 'RatingAnswer'},
            'answer': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rating_answers'", 'to': "orm['feedback.FeedbackRelation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': "orm['feedback.RatingQuestion']"})
        },
        'feedback.ratingquestion': {
            'Meta': {'object_name': 'RatingQuestion'},
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rating_questions'", 'to': "orm['feedback.Feedback']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '20'})
        },
        'feedback.textanswer': {
            'Meta': {'object_name': 'TextAnswer'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text_answers'", 'to': "orm['feedback.FeedbackRelation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': "orm['feedback.TextQuestion']"})
        },
        'feedback.textquestion': {
            'Meta': {'object_name': 'TextQuestion'},
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text_questions'", 'to': "orm['feedback.Feedback']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'})
        }
    }

    complete_apps = ['feedback']