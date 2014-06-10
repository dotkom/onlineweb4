# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'MultipleChoiceRelation.display'
        db.add_column(u'feedback_multiplechoicerelation', 'display',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Feedback.display_field_of_study'
        db.add_column(u'feedback_feedback', 'display_field_of_study',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'TextQuestion.display'
        db.add_column(u'feedback_textquestion', 'display',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'RatingQuestion.display'
        db.add_column(u'feedback_ratingquestion', 'display',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'MultipleChoiceRelation.display'
        db.delete_column(u'feedback_multiplechoicerelation', 'display')

        # Deleting field 'Feedback.display_field_of_study'
        db.delete_column(u'feedback_feedback', 'display_field_of_study')

        # Deleting field 'TextQuestion.display'
        db.delete_column(u'feedback_textquestion', 'display')

        # Deleting field 'RatingQuestion.display'
        db.delete_column(u'feedback_ratingquestion', 'display')


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
            'Meta': {'ordering': "['first_name', 'last_name']", 'object_name': 'OnlineUser'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'allergies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'compiled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'field_of_study': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'male'", 'max_length': '10'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infomail': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mark_rules': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ntnu_username': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'rfid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'started_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 3, 26, 0, 0)'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'feedback.choice': {
            'Meta': {'object_name': 'Choice'},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': u"orm['feedback.MultipleChoiceQuestion']"})
        },
        u'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authentication.OnlineUser']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'display_field_of_study': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feedback_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'feedback.feedbackrelation': {
            'Meta': {'unique_together': "(('feedback', 'content_type', 'object_id'),)", 'object_name': 'FeedbackRelation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'answered': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'feedbacks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['authentication.OnlineUser']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateField', [], {}),
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedback.Feedback']"}),
            'gives_mark': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'feedback.fieldofstudyanswer': {
            'Meta': {'object_name': 'FieldOfStudyAnswer'},
            'answer': ('django.db.models.fields.SmallIntegerField', [], {}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field_of_study_answers'", 'to': u"orm['feedback.FeedbackRelation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'feedback.multiplechoiceanswer': {
            'Meta': {'object_name': 'MultipleChoiceAnswer'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'multiple_choice_answers'", 'to': u"orm['feedback.FeedbackRelation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': u"orm['feedback.MultipleChoiceRelation']"})
        },
        u'feedback.multiplechoicequestion': {
            'Meta': {'object_name': 'MultipleChoiceQuestion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'feedback.multiplechoicerelation': {
            'Meta': {'object_name': 'MultipleChoiceRelation'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'multiple_choice_questions'", 'to': u"orm['feedback.Feedback']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiple_choice_relation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedback.MultipleChoiceQuestion']"}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '30'})
        },
        u'feedback.ratinganswer': {
            'Meta': {'object_name': 'RatingAnswer'},
            'answer': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rating_answers'", 'to': u"orm['feedback.FeedbackRelation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': u"orm['feedback.RatingQuestion']"})
        },
        u'feedback.ratingquestion': {
            'Meta': {'object_name': 'RatingQuestion'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rating_questions'", 'to': u"orm['feedback.Feedback']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '20'})
        },
        u'feedback.registertoken': {
            'Meta': {'object_name': 'RegisterToken'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fbr': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Feedback_relation'", 'to': u"orm['feedback.FeedbackRelation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'feedback.textanswer': {
            'Meta': {'object_name': 'TextAnswer'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text_answers'", 'to': u"orm['feedback.FeedbackRelation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': u"orm['feedback.TextQuestion']"})
        },
        u'feedback.textquestion': {
            'Meta': {'object_name': 'TextQuestion'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text_questions'", 'to': u"orm['feedback.Feedback']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'})
        }
    }

    complete_apps = ['feedback']