# Generated by Django 2.2.3 on 2019-08-06 21:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mail_collector', '0033_auto_20190806_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='ascii_address',
            field=models.BooleanField(default=True, help_text='Format internationalized DNS domains to ASCII. See https://tools.ietf.org/html/rfc5891 ', verbose_name='Force ASCII MX'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='backoff_factor',
            field=models.IntegerField(default=3, verbose_name='Back-off factor for check receive'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='check_mx',
            field=models.BooleanField(default=True, help_text='Ask the DNS server if the email domain is connectable', verbose_name='Verify MX connectivity'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='check_mx_timeout',
            field=models.DurationField(default=datetime.timedelta(0, 5), verbose_name='Verify MX timeout'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='email_subject',
            field=models.CharField(default='exchange monitoring message', max_length=78, verbose_name='Email Subject'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='is_default',
            field=models.BooleanField(db_index=True, default=False, verbose_name='is default?'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='mail_check_period',
            field=models.DurationField(default=datetime.timedelta(0, 3600), verbose_name='check email every'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='max_wait_receive',
            field=models.DurationField(default=datetime.timedelta(0, 120), verbose_name='Check receive timeout'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='min_wait_receive',
            field=models.DurationField(default=datetime.timedelta(0, 3), verbose_name='Wait before check receive'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='tags',
            field=models.TextField(blank=True, null=True, verbose_name='Optional tags'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='utf8_address',
            field=models.BooleanField(default=False, verbose_name='Allow UTF8 email address'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='witness_addresses',
            field=models.ManyToManyField(blank=True, limit_choices_to={'enabled': True}, to='mail_collector.WitnessEmail', verbose_name='Witness addresses'),
        ),
    ]
