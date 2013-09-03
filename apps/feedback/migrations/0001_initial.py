# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeedbackRelation'
        db.create_table(u'feedback_feedbackrelation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedback.Feedback'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'feedback', ['FeedbackRelation'])

        # Adding unique constraint on 'FeedbackRelation', fields ['feedback', 'content_type', 'object_id']
        db.create_unique(u'feedback_feedbackrelation', ['feedback_id', 'content_type_id', 'object_id'])

        # Adding M2M table for field answered on 'FeedbackRelation'
        db.create_table(u'feedback_feedbackrelation_answered', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feedbackrelation', models.ForeignKey(orm[u'feedback.feedbackrelation'], null=False)),
            ('onlineuser', models.ForeignKey(orm[u'authentication.onlineuser'], null=False))
        ))
        db.create_unique(u'feedback_feedbackrelation_answered', ['feedbackrelation_id', 'onlineuser_id'])

        # Adding model 'Feedback'
        db.create_table(u'feedback_feedback', (
            ('feedback_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.OnlineUser'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'feedback', ['Feedback'])

        # Adding model 'FieldOfStudyQuestion'
        db.create_table(u'feedback_fieldofstudyquestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(related_name='field_of_study_questions', to=orm['feedback.Feedback'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
        ))
        db.send_create_signal(u'feedback', ['FieldOfStudyQuestion'])

        # Adding model 'FieldOfStudyAnswer'
        db.create_table(u'feedback_fieldofstudyanswer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback_relation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='field_of_study_answers', to=orm['feedback.FeedbackRelation'])),
            ('answer', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answer', to=orm['feedback.FieldOfStudyQuestion'])),
        ))
        db.send_create_signal(u'feedback', ['FieldOfStudyAnswer'])

        # Adding model 'TextQuestion'
        db.create_table(u'feedback_textquestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(related_name='text_questions', to=orm['feedback.Feedback'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=10)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'feedback', ['TextQuestion'])

        # Adding model 'TextAnswer'
        db.create_table(u'feedback_textanswer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answer', to=orm['feedback.TextQuestion'])),
            ('feedback_relation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='text_answers', to=orm['feedback.FeedbackRelation'])),
            ('answer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'feedback', ['TextAnswer'])

        # Adding model 'RatingQuestion'
        db.create_table(u'feedback_ratingquestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rating_questions', to=orm['feedback.Feedback'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=20)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'feedback', ['RatingQuestion'])

        # Adding model 'RatingAnswer'
        db.create_table(u'feedback_ratinganswer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feedback_relation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rating_answers', to=orm['feedback.FeedbackRelation'])),
            ('answer', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answer', to=orm['feedback.RatingQuestion'])),
        ))
        db.send_create_signal(u'feedback', ['RatingAnswer'])


    def backwards(self, orm):
        # Removing unique constraint on 'FeedbackRelation', fields ['feedback', 'content_type', 'object_id']
        db.delete_unique(u'feedback_feedbackrelation', ['feedback_id', 'content_type_id', 'object_id'])

        # Deleting model 'FeedbackRelation'
        db.delete_table(u'feedback_feedbackrelation')

        # Removing M2M table for field answered on 'FeedbackRelation'
        db.delete_table('feedback_feedbackrelation_answered')

        # Deleting model 'Feedback'
        db.delete_table(u'feedback_feedback')

        # Deleting model 'FieldOfStudyQuestion'
        db.delete_table(u'feedback_fieldofstudyquestion')

        # Deleting model 'FieldOfStudyAnswer'
        db.delete_table(u'feedback_fieldofstudyanswer')

        # Deleting model 'TextQuestion'
        db.delete_table(u'feedback_textquestion')

        # Deleting model 'TextAnswer'
        db.delete_table(u'feedback_textanswer')

        # Deleting model 'RatingQuestion'
        db.delete_table(u'feedback_ratingquestion')

        # Deleting model 'RatingAnswer'
        db.delete_table(u'feedback_ratinganswer')


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
            'started_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 8, 22, 0, 0)'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authentication.OnlineUser']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'feedback_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'feedback.feedbackrelation': {
            'Meta': {'unique_together': "(('feedback', 'content_type', 'object_id'),)", 'object_name': 'FeedbackRelation'},
            'answered': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'feedbacks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['authentication.OnlineUser']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedback.Feedback']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'feedback.fieldofstudyanswer': {
            'Meta': {'object_name': 'FieldOfStudyAnswer'},
            'answer': ('django.db.models.fields.SmallIntegerField', [], {}),
            'feedback_relation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field_of_study_answers'", 'to': u"orm['feedback.FeedbackRelation']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answer'", 'to': u"orm['feedback.FieldOfStudyQuestion']"})
        },
        u'feedback.fieldofstudyquestion': {
            'Meta': {'object_name': 'FieldOfStudyQuestion'},
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field_of_study_questions'", 'to': u"orm['feedback.Feedback']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
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
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rating_questions'", 'to': u"orm['feedback.Feedback']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '20'})
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
            'feedback': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text_questions'", 'to': u"orm['feedback.Feedback']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'})
        }
    }

    complete_apps = ['feedback']