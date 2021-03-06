# Generated by Django 2.2.6 on 2020-07-22 18:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import p_soc_auto_base.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ssl_cert_tracker', '0013_auto_20200420_0928'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalSslNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True, help_text='object creation time stamp', verbose_name='created on')),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True, help_text='object update time stamp', verbose_name='updated on')),
                ('enabled', models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('address', models.CharField(db_index=True, max_length=256, verbose_name='address of the SSL node')),
                ('created_by', models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='ssl_cert_tracker_externalsslnode_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('updated_by', models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='ssl_cert_tracker_externalsslnode_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
            ],
            options={
                'verbose_name': 'External node monitored for SSL certificates',
            },
        ),
    ]
