# Generated by Django 2.2.6 on 2020-04-20 16:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import p_soc_auto_base.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail_collector', '0044_auto_20200311_0913'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangeserver',
            name='created_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_exchangeserver_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='exchangeserver',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, help_text='object creation time stamp', verbose_name='created on'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exchangeserver',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='notes'),
        ),
        migrations.AddField(
            model_name='exchangeserver',
            name='updated_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_exchangeserver_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='exchangeserver',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='object update time stamp', verbose_name='updated on'),
        ),
        migrations.AddField(
            model_name='mailbetweendomains',
            name='created_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_mailbetweendomains_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='mailbetweendomains',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, help_text='object creation time stamp', verbose_name='created on'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mailbetweendomains',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='notes'),
        ),
        migrations.AddField(
            model_name='mailbetweendomains',
            name='updated_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_mailbetweendomains_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='mailbetweendomains',
            name='updated_on',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='object update time stamp', verbose_name='updated on'),
        ),
        migrations.AlterField(
            model_name='domainaccount',
            name='created_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_domainaccount_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='domainaccount',
            name='updated_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_domainaccount_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AlterField(
            model_name='exchangeaccount',
            name='created_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_exchangeaccount_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='exchangeaccount',
            name='updated_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_exchangeaccount_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='created_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_exchangeconfiguration_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='exchangeconfiguration',
            name='updated_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_exchangeconfiguration_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AlterField(
            model_name='exchangeserver',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
        migrations.AlterField(
            model_name='mailbetweendomains',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
        migrations.AlterField(
            model_name='witnessemail',
            name='created_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_witnessemail_created_by_related', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='witnessemail',
            name='updated_by',
            field=models.ForeignKey(default=p_soc_auto_base.utils.get_default_user_id, on_delete=django.db.models.deletion.PROTECT, related_name='mail_collector_witnessemail_updated_by_related', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
    ]