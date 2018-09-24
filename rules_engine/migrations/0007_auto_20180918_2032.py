# Generated by Django 2.1.1 on 2018-09-18 20:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('rules_engine', '0006_auto_20180911_2051'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notificationeventforruledemo',
            options={'verbose_name': 'Place holder for notifications', 'verbose_name_plural': 'Place holder for notifications'},
        ),
        migrations.AlterModelOptions(
            name='ruleapplies',
            options={'verbose_name': 'Content to which a Rule Applies', 'verbose_name_plural': 'Content to which a Rule Applies'},
        ),
        migrations.AlterModelOptions(
            name='tindataforruledemos',
            options={'verbose_name': 'Sample data for demonstrating rules', 'verbose_name_plural': 'Sample data for demonstrating rules'},
        ),
        migrations.AlterField(
            model_name='notificationeventforruledemo',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='applies',
            field=models.ManyToManyField(through='rules_engine.RuleApplies', to='contenttypes.ContentType', verbose_name='This Rule Applies to'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
        migrations.AlterField(
            model_name='ruleapplies',
            name='content_type',
            field=models.ForeignKey(help_text='Links a rule to a model to which the rule applies to', on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Content Type'),
        ),
        migrations.AlterField(
            model_name='ruleapplies',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
        migrations.AlterField(
            model_name='tindataforruledemos',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
        migrations.AlterUniqueTogether(
            name='ruleapplies',
            unique_together={('rule', 'content_type', 'field_name')},
        ),
    ]
