# Generated by Django 2.2.6 on 2019-12-27 19:23

from django.db import migrations


def delete_beats(apps, schema_editor):
    old_beats = [
        ('AD controller monitoring: perf alert summary report, full bind, orion'),
        ('AD controller monitoring: perf alert summary report, anon bind, orion'),
        ('AD controller monitoring: perf alert summary report, full bind, non orion'),
        ('AD controller monitoring: perf alert summary report, anon bind, non orion'),
        ('AD controller monitoring: perf warning summary report, full bind, orion'),
        ('AD controller monitoring: perf warning summary report, anon bind, orion'),
        ('AD controller monitoring: perf warning summary report, full bind, non orion'),
        ('AD controller monitoring: perf warning summary report, anon bind, non orion'),
    ]

    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')

    PeriodicTask.objects.filter(name__in=old_beats).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ldap_probe', '0038_maintain_nodes_beat'),
    ]

    operations = [
        migrations.RunPython(
            delete_beats, reverse_code=migrations.RunPython.noop),
    ]
