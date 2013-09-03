# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("authentication", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'FeedbackRelation'
        db.create_table('feedback_feedbackrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedback.Feedback'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('feedback', ['FeedbackRelation'])

        # Adding unique constraint on 'FeedbackRelation', fields ['feedback', 'content_type', 'object_id']
        db.create_unique('feedback_feedbackrelation', ['feedback_id', 'content_type_id', 'object_id'])

        # Adding M2M table for field answered on 'FeedbackRelation'
        db.create_table('feedback_feedbackrelation_answered', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feedbackrelation', models.ForeignKey(orm['feedback.feedbackrelation'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('feedback_feedbackrelation_answered', ['feedbackrelation_id', 'user_id'])

        # Adding model 'Feedback'
        db.create_table('feedback_feedback', (
            ('feedback_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('feedback', ['Feedback'])

        # Adding model 'FieldOfStudyQuestion'
        db.create_table('feedback_fieldofstudyquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(related_name='field_of_study_questions', to=orm['feedback.Feedback'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
        ))
        db.send_create_signal('feedback', ['FieldOfStudyQuestion'])

        # Adding model 'FieldOfStudyAnswer'
        db.create_table('feedback_fieldofstudyanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback_relation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='field_of_study_answers', to=orm['feedback.FeedbackRelation'])),
            ('answer', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answer', to=orm['feedback.FieldOfStudyQuestion'])),
        ))
        db.send_create_signal('feedback', ['FieldOfStudyAnswer'])

        # Adding model 'TextQuestion'
        db.create_table('feedback_textquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(related_name='text_questions', to=orm['feedback.Feedback'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=10)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('feedback', ['TextQuestion'])

        # Adding model 'TextAnswer'
        db.create_table('feedback_textanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answer', to=orm['feedback.TextQuestion'])),
            ('feedback_relation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='text_answers', to=orm['feedback.FeedbackRelation'])),
            ('answer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('feedback', ['TextAnswer'])

        # Adding model 'RatingQuestion'
        db.create_table('feedback_ratingquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rating_questions', to=orm['feedback.Feedback'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=20)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('feedback', ['RatingQuestion'])

        # Adding model 'RatingAnswer'
        db.create_table('feedback_ratinganswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback_relation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rating_answers', to=orm['feedback.FeedbackRelation'])),
            ('answer', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answer', to=orm['feedback.RatingQuestion'])),
        ))
        db.send_create_signal('feedback', ['RatingAnswer'])


    def backwards(self, orm):
        # Removing unique constraint on 'FeedbackRelation', fields ['feedback', 'content_type', 'object_id']
        db.delete_unique('feedback_feedbackrelation', ['feedback_id', 'content_type_id', 'object_id'])

        # Deleting model 'FeedbackRelation'
        db.delete_table('feedback_feedbackrelation')

        # Removing M2M table for field answered on 'FeedbackRelation'
        db.delete_table('feedback_feedbackrelation_answered')

        # Deleting model 'Feedback'
        db.delete_table('feedback_feedback')

        # Deleting model 'FieldOfStudyQuestion'
        db.delete_table('feedback_fieldofstudyquestion')

        # Deleting model 'FieldOfStudyAnswer'
        db.delete_table('feedback_fieldofstudyanswer')

        # Deleting model 'TextQuestion'
        db.delete_table('feedback_textquestion')

        # Deleting model 'TextAnswer'
        db.delete_table('feedback_textanswer')

        # Deleting model 'RatingQuestion'
        db.delete_table('feedback_ratingquestion')

        # Deleting model 'RatingAnswer'
        db.delete_table('feedback_ratinganswer')


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
            'answered': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'feedbacks'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['feedback.Feedback']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
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
