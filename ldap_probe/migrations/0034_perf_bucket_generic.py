# Generated by Django 2.2.6 on 2019-12-17 23:15
import decimal

from django.contrib.auth.models import User, UserManager
from django.db import migrations


def add_perf_buckets(apps, schema_editor):
    PerfBucket = apps.get_model('ldap_probe', 'ADNodePerfBucket')

    user = User.objects.filter(is_superuser=True)
    if user.exists():
        user = user.first()
    else:
        user = User.objects.create(
            username='soc_su', email='soc_su@phsa.ca',
            password='soc_su_password', is_active=True, is_staff=True,
            is_superuser=True)
        user.set_password('soc_su_password')
        user.save()

    user_dict = {'created_by_id': user.id,
                 'updated_by_id': user.id, }

    perf_buckets = [
        {'location': 'generic default location',
         'avg_warn_threshold': decimal.Decimal('0.500'),
         'avg_err_threshold': decimal.Decimal('0.750'),
         'alert_threshold': decimal.Decimal('1.000'),
         'notes': 'place holder, please update',
         'is_default': True,
         }, ]

    for perf_bucket in perf_buckets:
        perf_bucket.update(user_dict)
        new_perf_bucket = PerfBucket(**perf_bucket)
        new_perf_bucket.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ldap_probe', '0033_auto_20191217_1435'),
    ]

    operations = [
        migrations.RunPython(add_perf_buckets,
                             reverse_code=migrations.RunPython.noop)
    ]
