# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
            ],
            options={
                'permissions': (('view_abstractvote', 'View AbstractVote'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AbstractVoter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'permissions': (('view_abstractvoter', 'View AbstractVoter'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Alternative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alt_id', models.PositiveIntegerField(help_text='Alternativ ID')),
                ('description', models.CharField(max_length=150, null=True, verbose_name='Beskrivelse', blank=True)),
            ],
            options={
                'permissions': (('view_alternative', 'View Alternative'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnonymousVoter',
            fields=[
                ('abstractvoter_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='genfors.AbstractVoter')),
                ('user_hash', models.CharField(max_length=64)),
            ],
            options={
                'permissions': (('view_anonymousvoter', 'View AnonymousVoter'),),
            },
            bases=('genfors.abstractvoter',),
        ),
        migrations.CreateModel(
            name='BooleanVote',
            fields=[
                ('abstractvote_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='genfors.AbstractVote')),
                ('answer', models.NullBooleanField(help_text='Ja/Nei', verbose_name='answer')),
            ],
            options={
                'permissions': (('view_booleanvote', 'View BooleanVote'),),
            },
            bases=('genfors.abstractvote',),
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(help_text='Tidspunkt for arrangementsstart', verbose_name='Tidspunkt')),
                ('title', models.CharField(max_length=150, verbose_name='Tittel')),
                ('registration_locked', models.BooleanField(default=True, help_text='Steng registrering', verbose_name='registration_lock')),
                ('ended', models.BooleanField(default=False, help_text='Avslutt generalforsamlingen', verbose_name='event_lockdown')),
                ('pin', models.CharField(default=b'stub', max_length=8, verbose_name='Pinkode')),
            ],
            options={
                'verbose_name': 'Generalforsamling',
                'verbose_name_plural': 'Generalforsamlinger',
                'permissions': (('view_meeting', 'View Meeting'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoice',
            fields=[
                ('abstractvote_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='genfors.AbstractVote')),
                ('answer', models.ForeignKey(blank=True, to='genfors.Alternative', help_text='Alternativ', null=True)),
            ],
            options={
                'permissions': (('view_multiplechoice', 'View MultipleChoice'),),
            },
            bases=('genfors.abstractvote',),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anonymous', models.BooleanField(default=False, verbose_name='Hemmelig valg')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='added')),
                ('locked', models.BooleanField(default=False, help_text='Steng avstemmingen', verbose_name='locked')),
                ('question_type', models.SmallIntegerField(default=0, verbose_name='Sp\xf8rsm\xe5lstype', choices=[(0, 'Ja/Nei'), (1, 'Multiple Choice')])),
                ('description', models.TextField(help_text='Beskrivelse av saken som skal stemmes over', max_length=500, verbose_name='Beskrivelse', blank=True)),
                ('majority_type', models.SmallIntegerField(default=0, verbose_name='Flertallstype', choices=[(0, 'Alminnelig flertall (1/2)'), (1, 'Kvalifisert flertall (2/3)')])),
                ('only_show_winner', models.BooleanField(default=False, verbose_name='Vis kun vinner')),
                ('total_voters', models.IntegerField(null=True, verbose_name='Stemmeberettigede')),
                ('meeting', models.ForeignKey(help_text='Generalforsamling', to='genfors.Meeting')),
            ],
            options={
                'permissions': (('view_question', 'View Question'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegisteredVoter',
            fields=[
                ('abstractvoter_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='genfors.AbstractVoter')),
                ('can_vote', models.BooleanField(default=False, help_text='Har stemmerett', verbose_name='voting_right')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_registeredvoter', 'View RegisteredVoter'),),
            },
            bases=('genfors.abstractvoter',),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_public', models.TextField(max_length=2000)),
                ('result_private', models.TextField(max_length=2000)),
                ('meeting', models.ForeignKey(help_text='Meeting', to='genfors.Meeting')),
                ('question', models.ForeignKey(help_text='Meeting', to='genfors.Question')),
            ],
            options={
                'permissions': (('view_result', 'View Result'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='alternative',
            name='question',
            field=models.ForeignKey(help_text='Question', to='genfors.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='abstractvoter',
            name='meeting',
            field=models.ForeignKey(to='genfors.Meeting'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='abstractvote',
            name='question',
            field=models.ForeignKey(to='genfors.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='abstractvote',
            name='voter',
            field=models.ForeignKey(help_text='Bruker', to='genfors.AbstractVoter'),
            preserve_default=True,
        ),
    ]
