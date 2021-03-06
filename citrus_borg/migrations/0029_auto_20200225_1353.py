# Generated by Django 2.2.6 on 2020-02-25 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citrus_borg', '0028_merge_20200121_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='winlogevent',
            name='event_id',
            field=models.BigIntegerField(blank=True, db_index=True, help_text='the type of the event represented by this log', null=True, verbose_name='Event ID'),
        ),
        migrations.AddField(
            model_name='winlogevent',
            name='timestamp',
            field=models.DateTimeField(blank=True, db_index=True, help_text='windows log event creation time stamp', null=True, verbose_name='Timestamp'),
        ),
    ]
