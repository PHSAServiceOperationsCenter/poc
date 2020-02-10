# Generated by Django 2.2.6 on 2019-11-15 22:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import ldap_probe.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ldap_probe', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ldapprobelog',
            old_name='elapsed_searc_ext',
            new_name='elapsed_search_ext',
        ),
        migrations.AddField(
            model_name='ldapprobelog',
            name='ad_response',
            field=models.TextField(blank=True, null=True,
                                   verbose_name='AD controller response'),
        ),
        migrations.AlterField(
            model_name='nonorionadnode',
            name='ldap_bind_cred',
            field=models.ForeignKey(default=ldap_probe.models.LDAPBindCred.get_default, on_delete=django.db.models.deletion.PROTECT,
                                    to='ldap_probe.LDAPBindCred', verbose_name='LDAP Bind Credentials'),
        ),
        migrations.AlterField(
            model_name='orionadnode',
            name='ldap_bind_cred',
            field=models.ForeignKey(default=ldap_probe.models.LDAPBindCred.get_default, on_delete=django.db.models.deletion.PROTECT,
                                    to='ldap_probe.LDAPBindCred', verbose_name='LDAP Bind Credentials'),
        ),
        migrations.CreateModel(
            name='LdapCredError',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True,
                                                    help_text='object creation time stamp', verbose_name='created on')),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True,
                                                    help_text='object update time stamp', verbose_name='updated on')),
                ('enabled', models.BooleanField(db_index=True, default=True,
                                                help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled')),
                ('notes', models.TextField(
                    blank=True, null=True, verbose_name='notes')),
                ('error_unique_identifier', models.CharField(db_index=True,
                                                             max_length=3, unique=True, verbose_name='LDAP Error Subcode')),
                ('short_descriptiom', models.CharField(db_index=True,
                                                       max_length=128, verbose_name='Short Description')),
                ('comments', models.TextField(
                    blank=True, null=True, verbose_name='Comments')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                                 related_name='ldap_probe_ldapcrederror_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                                 related_name='ldap_probe_ldapcrederror_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
            ],
            options={
                'verbose_name': 'Active Directory Bind Error',
                'verbose_name_plural': 'Common Active Directory Bind Errors',
            },
        ),
    ]
