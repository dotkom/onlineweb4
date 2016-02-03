# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companyprofile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('attended', models.BooleanField(default=False, verbose_name='var tilstede')),
                ('paid', models.BooleanField(default=False, verbose_name='har betalt')),
                ('note', models.CharField(default=b'', max_length=100, verbose_name='notat', blank=True)),
            ],
            options={
                'ordering': ['timestamp'],
                'permissions': (('view_attendee', 'View Attendee'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompanyEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.ForeignKey(verbose_name='bedrifter', to='companyprofile.Company')),
            ],
            options={
                'verbose_name': 'bedrift',
                'verbose_name_plural': 'bedrifter',
                'permissions': (('view_companyevent', 'View CompanyEvent'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60, verbose_name='tittel')),
                ('event_start', models.DateTimeField(verbose_name='start-dato')),
                ('event_end', models.DateTimeField(verbose_name='slutt-dato')),
                ('location', models.CharField(max_length=100, verbose_name='lokasjon')),
                ('ingress_short', models.CharField(max_length=150, verbose_name='kort ingress')),
                ('ingress', models.TextField(verbose_name='ingress')),
                ('description', models.TextField(verbose_name='beskrivelse')),
                ('image', filebrowser.fields.FileBrowseField(max_length=200, null=True, verbose_name='bilde', blank=True)),
                ('event_type', models.SmallIntegerField(verbose_name='type', choices=[(1, b'Sosialt'), (2, b'Bedriftspresentasjon'), (3, b'Kurs'), (4, b'Utflukt'), (5, b'Ekskursjon'), (6, b'Internt'), (7, b'Annet')])),
            ],
            options={
                'verbose_name': 'arrangement',
                'verbose_name_plural': 'arrangement',
                'permissions': (('view_event', 'View Event'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AttendanceEvent',
            fields=[
                ('event', models.OneToOneField(related_name='attendance_event', primary_key=True, serialize=False, to='events.Event')),
                ('max_capacity', models.PositiveIntegerField(verbose_name='maks-kapasitet')),
                ('waitlist', models.BooleanField(default=False, verbose_name='venteliste')),
                ('guest_attendance', models.BooleanField(default=False, verbose_name='gjestep\xe5melding')),
                ('registration_start', models.DateTimeField(verbose_name='registrerings-start')),
                ('unattend_deadline', models.DateTimeField(verbose_name='avmeldings-frist')),
                ('registration_end', models.DateTimeField(verbose_name='registrerings-slutt')),
                ('automatically_set_marks', models.BooleanField(default=False, help_text='P\xe5meldte som ikke har m\xf8tt vil automatisk f\xe5 prikk', verbose_name='automatisk prikk')),
                ('marks_has_been_set', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'p\xe5melding',
                'verbose_name_plural': 'p\xe5meldinger',
                'permissions': (('view_attendanceevent', 'View AttendanceEvent'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seats', models.PositiveIntegerField(verbose_name='reserverte plasser')),
                ('attendance_event', models.OneToOneField(related_name='reserved_seats', to='events.AttendanceEvent')),
            ],
            options={
                'verbose_name': 'reservasjon',
                'verbose_name_plural': 'reservasjoner',
                'permissions': (('view_reservation', 'View Reservation'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reservee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=69, verbose_name='navn')),
                ('note', models.CharField(max_length=100, verbose_name='notat')),
                ('allergies', models.CharField(max_length=200, null=True, verbose_name='allergier', blank=True)),
                ('reservation', models.ForeignKey(related_name='reservees', to='events.Reservation')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'reservasjon',
                'verbose_name_plural': 'reservasjoner',
                'permissions': (('view_reservee', 'View Reservee'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('offset', models.PositiveSmallIntegerField(default=0, help_text='utsettelse oppgis i timer', verbose_name='utsettelse')),
            ],
            options={
                'permissions': (('view_rule', 'View Rule'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GradeRule',
            fields=[
                ('rule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='events.Rule')),
                ('grade', models.SmallIntegerField(verbose_name='klassetrinn')),
            ],
            options={
                'permissions': (('view_graderule', 'View GradeRule'),),
            },
            bases=('events.rule',),
        ),
        migrations.CreateModel(
            name='FieldOfStudyRule',
            fields=[
                ('rule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='events.Rule')),
                ('field_of_study', models.SmallIntegerField(verbose_name='studieretning', choices=[(0, 'Gjest'), (1, 'Bachelor i Informatikk (BIT)'), (10, 'Software (SW)'), (11, 'Informasjonsforvaltning (DIF)'), (12, 'Komplekse Datasystemer (KDS)'), (13, 'Spillteknologi (SPT)'), (14, 'Intelligente Systemer (IRS)'), (15, 'Helseinformatikk (MSMEDTEK)'), (30, 'Annen mastergrad'), (80, 'PhD'), (90, 'International'), (100, 'Annet Onlinemedlem')])),
            ],
            options={
                'permissions': (('view_fieldofstudyrule', 'View FieldOfStudyRule'),),
            },
            bases=('events.rule',),
        ),
        migrations.CreateModel(
            name='RuleBundle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100, null=True, verbose_name='beskrivelse', blank=True)),
                ('field_of_study_rules', models.ManyToManyField(to='events.FieldOfStudyRule', null=True, blank=True)),
                ('grade_rules', models.ManyToManyField(to='events.GradeRule', null=True, blank=True)),
            ],
            options={
                'permissions': (('view_rulebundle', 'View RuleBundle'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserGroupRule',
            fields=[
                ('rule_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='events.Rule')),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'permissions': (('view_usergrouprule', 'View UserGroupRule'),),
            },
            bases=('events.rule',),
        ),
        migrations.AddField(
            model_name='rulebundle',
            name='user_group_rules',
            field=models.ManyToManyField(to='events.UserGroupRule', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='author',
            field=models.ForeignKey(related_name='oppretter', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyevent',
            name='event',
            field=models.ForeignKey(related_name='companies', verbose_name='arrangement', to='events.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendee',
            name='event',
            field=models.ForeignKey(related_name='attendees', to='events.AttendanceEvent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendee',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='attendee',
            unique_together=set([('event', 'user')]),
        ),
        migrations.AddField(
            model_name='attendanceevent',
            name='rule_bundles',
            field=models.ManyToManyField(to='events.RuleBundle', null=True, blank=True),
            preserve_default=True,
        ),
    ]
