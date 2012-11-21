# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Feedback'
        db.create_table('feedback_feedback', (
            ('feedback_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='oppretter', to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('feedback', ['Feedback'])

        # Adding model 'Question'
        db.create_table('feedback_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('feedback', ['Question'])

        # Adding model 'FieldOfStudyQuestion'
        db.create_table('feedback_fieldofstudyquestion', (
            ('question_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['feedback.Question'], unique=True)),
            ('feedback', self.gf('django.db.models.fields.related.OneToOneField')(related_name='field_of_study', unique=True, primary_key=True, to=orm['feedback.Feedback'])),
            ('field_of_study', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('feedback', ['FieldOfStudyQuestion'])

        # Adding model 'TextQuestion'
        db.create_table('feedback_textquestion', (
            ('question_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['feedback.Question'], unique=True, primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(related_name='text', to=orm['feedback.Feedback'])),
            ('label', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('feedback', ['TextQuestion'])

        # Adding model 'Answer'
        db.create_table('feedback_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answer', to=orm['feedback.Question'])),
        ))
        db.send_create_signal('feedback', ['Answer'])

        # Adding model 'TextAnswer'
        db.create_table('feedback_textanswer', (
            ('answer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['feedback.Answer'], unique=True, primary_key=True)),
            ('answer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('feedback', ['TextAnswer'])

        # Adding model 'FieldOfStudyAnswer'
        db.create_table('feedback_fieldofstudyanswer', (
            ('answer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['feedback.Answer'], unique=True, primary_key=True)),
            ('answer', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('feedback', ['FieldOfStudyAnswer'])

        # Adding model 'FeedbackToObjectRelation'
        db.create_table('feedback_feedbacktoobjectrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['feedback.Feedback'], unique=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('feedback', ['FeedbackToObjectRelation'])

        # Adding unique constraint on 'FeedbackToObjectRelation', fields ['feedback_id', 'content_type', 'object_id']
        db.create_unique('feedback_feedbacktoobjectrelation', ['feedback_id_id', 'content_type_id', 'object_id'])

        # Adding M2M table for field answered on 'FeedbackToObjectRelation'
        db.create_table('feedback_feedbacktoobjectrelation_answered', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feedbacktoobjectrelation', models.ForeignKey(orm['feedback.feedbacktoobjectrelation'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('feedback_feedbacktoobjectrelation_answered', ['feedbacktoobjectrelation_id', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FeedbackToObjectRelation', fields ['feedback_id', 'content_type', 'object_id']
        db.delete_unique('feedback_feedbacktoobjectrelation', ['feedback_id_id', 'content_type_id', 'object_id'])

        # Deleting model 'Feedback'
        db.delete_table('feedback_feedback')

        # Deleting model 'Question'
        db.delete_table('feedback_question')

        # Deleting model 'FieldOfStudyQuestion'
        db.delete_table('feedback_fieldofstudyquestion')

        # Deleting model 'TextQuestion'
        db.delete_table('feedback_textquestion')

        # Deleting model 'Answer'
        db.delete_table('feedback_answer')

        # Deleting model 'TextAnswer'
        db.delete_table('feedback_textanswer')

        # Deleting model 'FieldOfStudyAnswer'
        db.delete_table('feedback_fieldofstudyanswer')

        # Deleting model 'FeedbackToObjectRelation'
        db.delete_table('feedback_feedbacktoobjectrelation')

        # Removing M2M table for field answered on 'FeedbackToObjectRelation'
        db.delete_table('feedback_feedbacktoobjectrelation_answered')


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
        'feedback.answer': {
            'Meta': {'object_name': 'Answer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': "orm['feedback.Question']"})
        },
        'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'oppretter'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'feedback_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'feedback.feedbacktoobjectrelation': {
            'Meta': {'unique_together': "(('feedback_id', 'content_type', 'object_id'),)", 'object_name': 'FeedbackToObjectRelation'},
            'answered': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'feedbacks'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'feedback_id': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['feedback.Feedback']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'feedback.fieldofstudyanswer': {
            'Meta': {'object_name': 'FieldOfStudyAnswer', '_ormbases': ['feedback.Answer']},
            'answer': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'answer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['feedback.Answer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'feedback.fieldofstudyquestion': {
            'Meta': {'object_name': 'FieldOfStudyQuestion', '_ormbases': ['feedback.Question']},
            'feedback': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'field_of_study'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['feedback.Feedback']"}),
            'field_of_study': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'question_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['feedback.Question']", 'unique': 'True'})
        },
        'feedback.question': {
            'Meta': {'object_name': 'Question'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'feedback.textanswer': {
            'Meta': {'object_name': 'TextAnswer', '_ormbases': ['feedback.Answer']},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'answer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['feedback.Answer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'feedback.textquestion': {
            'Meta': {'object_name': 'TextQuestion', '_ormbases': ['feedback.Question']},
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text'", 'to': "orm['feedback.Feedback']"}),
            'label': ('django.db.models.fields.TextField', [], {}),
            'question_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['feedback.Question']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['feedback']