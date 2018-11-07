# Generated by Django 2.1.1 on 2018-10-24 22:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ssl_cert_tracker', '0002_auto_20181024_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalNmapCertsData',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, db_index=True, editable=False, help_text='object creation time stamp', verbose_name='created on')),
                ('updated_on', models.DateTimeField(blank=True, db_index=True, editable=False, help_text='object update time stamp', verbose_name='updated on')),
                ('enabled', models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('node_id', models.BigIntegerField(db_index=True, help_text='this is the primary keyof the orion node instance as defined in the orion_integration application', verbose_name='orion node local id')),
                ('addresses', models.CharField(max_length=100)),
                ('not_before', models.DateTimeField(db_index=True, help_text='certificate not valid before this date', verbose_name='not before')),
                ('not_after', models.DateTimeField(db_index=True, help_text='certificate not valid after this date', verbose_name='not after')),
                ('xml_data', models.TextField()),
                ('common_name', models.CharField(db_index=True, help_text='the CN part of an SSL certificate', max_length=100, verbose_name='common name')),
                ('organization_name', models.CharField(blank=True, db_index=True, help_text='the O part of the SSL certificate', max_length=100, null=True, verbose_name='organization')),
                ('country_name', models.CharField(blank=True, max_length=100, null=True)),
                ('sig_algo', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('bits', models.CharField(blank=True, max_length=100, null=True)),
                ('md5', models.CharField(db_index=True, max_length=100, verbose_name='md5')),
                ('sha1', models.CharField(db_index=True, max_length=100, verbose_name='sha1')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('created_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical SSL Certificate',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
