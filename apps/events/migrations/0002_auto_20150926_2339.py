# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendanceevent',
            name='rule_bundles',
            field=models.ManyToManyField(to='events.RuleBundle', blank=True),
        ),
        migrations.AlterField(
            model_name='rulebundle',
            name='field_of_study_rules',
            field=models.ManyToManyField(to='events.FieldOfStudyRule', blank=True),
        ),
        migrations.AlterField(
            model_name='rulebundle',
            name='grade_rules',
            field=models.ManyToManyField(to='events.GradeRule', blank=True),
        ),
        migrations.AlterField(
            model_name='rulebundle',
            name='user_group_rules',
            field=models.ManyToManyField(to='events.UserGroupRule', blank=True),
        ),
    ]
