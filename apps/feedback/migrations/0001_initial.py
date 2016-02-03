# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=256, verbose_name='valg')),
            ],
            options={
                'permissions': (('view_choice', 'View Choice'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('feedback_id', models.AutoField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=100, verbose_name='beskrivelse')),
                ('display_field_of_study', models.BooleanField(default=True, help_text='Grafen over studiefelt vil bli vist til bedriften', verbose_name='Vis studie oversikt')),
                ('display_info', models.BooleanField(default=True, help_text='En boks med ekstra informasjon vil bli vist til bedriften', verbose_name='Vis extra informasjon')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'tilbakemeldingsskjema',
                'verbose_name_plural': 'tilbakemeldingsskjemaer',
                'permissions': (('view_feedback', 'View Feedback'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedbackRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('deadline', models.DateField(verbose_name='Tidsfrist')),
                ('gives_mark', models.BooleanField(default=True, help_text='Gir automatisk prikk til brukere som ikke har svart innen fristen', verbose_name='Gir Prikk')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('first_mail_sent', models.BooleanField(default=False)),
                ('answered', models.ManyToManyField(related_name='feedbacks', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('feedback', models.ForeignKey(verbose_name='Tilbakemeldingskjema', to='feedback.Feedback')),
            ],
            options={
                'verbose_name': 'tilbakemelding',
                'verbose_name_plural': 'tilbakemeldinger',
                'permissions': (('view_feedbackrelation', 'View FeedbackRelation'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldOfStudyAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.SmallIntegerField(verbose_name='Studieretning', choices=[(0, 'Gjest'), (1, 'Bachelor i Informatikk (BIT)'), (10, 'Software (SW)'), (11, 'Informasjonsforvaltning (DIF)'), (12, 'Komplekse Datasystemer (KDS)'), (13, 'Spillteknologi (SPT)'), (14, 'Intelligente Systemer (IRS)'), (15, 'Helseinformatikk (MSMEDTEK)'), (30, 'Annen mastergrad'), (80, 'PhD'), (90, 'International'), (100, 'Annet Onlinemedlem')])),
                ('feedback_relation', models.ForeignKey(related_name='field_of_study_answers', to='feedback.FeedbackRelation')),
            ],
            options={
                'permissions': (('view_fieldofstudyanswer', 'View FieldOfStudyAnswer'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoiceAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.CharField(max_length=256, verbose_name='svar')),
                ('feedback_relation', models.ForeignKey(related_name='multiple_choice_answers', to='feedback.FeedbackRelation')),
            ],
            options={
                'permissions': (('view_multiplechoiceanswer', 'View MultipleChoiceAnswer'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoiceQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=256, verbose_name='Sp\xf8rsm\xe5l')),
            ],
            options={
                'permissions': (('view_multiplechoicequestion', 'View MultipleChoiceQuestion'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoiceRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.SmallIntegerField(default=30, verbose_name='Rekkef\xf8lge')),
                ('display', models.BooleanField(default=True, verbose_name='Vis til bedrift')),
                ('feedback', models.ForeignKey(related_name='multiple_choice_questions', to='feedback.Feedback')),
                ('multiple_choice_relation', models.ForeignKey(to='feedback.MultipleChoiceQuestion')),
            ],
            options={
                'permissions': (('view_multiplechoicerelation', 'View MultipleChoiceRelation'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RatingAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.SmallIntegerField(default=0, verbose_name='karakter', choices=[(1, b'1'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5'), (6, b'6')])),
                ('feedback_relation', models.ForeignKey(related_name='rating_answers', to='feedback.FeedbackRelation')),
            ],
            options={
                'permissions': (('view_ratinganswer', 'View RatingAnswer'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RatingQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.SmallIntegerField(default=20, verbose_name='Rekkef\xf8lge')),
                ('label', models.CharField(max_length=256, verbose_name='Sp\xf8rsm\xe5l')),
                ('display', models.BooleanField(default=True, verbose_name='Vis til bedrift')),
                ('feedback', models.ForeignKey(related_name='rating_questions', to='feedback.Feedback')),
            ],
            options={
                'permissions': (('view_ratingquestion', 'View RatingQuestion'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegisterToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=32, verbose_name='token')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='opprettet dato')),
                ('fbr', models.ForeignKey(related_name='Feedback_relation', to='feedback.FeedbackRelation')),
            ],
            options={
                'permissions': (('view_feedbackregistertoken', 'View FeedbackRegisterToken'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.TextField(verbose_name='svar')),
                ('feedback_relation', models.ForeignKey(related_name='text_answers', to='feedback.FeedbackRelation')),
            ],
            options={
                'permissions': (('view_textanswer', 'View TextAnswer'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.SmallIntegerField(default=10, verbose_name='Rekkef\xf8lge')),
                ('label', models.CharField(max_length=256, verbose_name='Sp\xf8rsm\xe5l')),
                ('display', models.BooleanField(default=True, verbose_name='Vis til bedrift')),
                ('feedback', models.ForeignKey(related_name='text_questions', to='feedback.Feedback')),
            ],
            options={
                'permissions': (('view_textquestion', 'View TextQuestion'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='textanswer',
            name='question',
            field=models.ForeignKey(related_name='answer', to='feedback.TextQuestion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ratinganswer',
            name='question',
            field=models.ForeignKey(related_name='answer', to='feedback.RatingQuestion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoiceanswer',
            name='question',
            field=models.ForeignKey(related_name='answer', to='feedback.MultipleChoiceRelation'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='feedbackrelation',
            unique_together=set([('feedback', 'content_type', 'object_id')]),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(related_name='choices', to='feedback.MultipleChoiceQuestion'),
            preserve_default=True,
        ),
    ]
