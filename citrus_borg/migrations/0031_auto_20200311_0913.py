# Generated by Django 2.2.6 on 2020-03-11 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('citrus_borg', '0030_auto_20200227_1546'),
    ]

    operations = [
        migrations.RenameField(
            model_name='winlogbeathost',
            old_name='excgh_last_seen',
            new_name='exchange_last_seen',
        ),
    ]
