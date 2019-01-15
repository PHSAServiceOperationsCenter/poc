# Generated by Django 2.1.4 on 2019-01-07 17:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ssl_cert_tracker', '0015_auto_20181212_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalnmapcertsdata',
            name='created_by',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='historicalnmapcertsdata',
            name='updated_by',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
    ]