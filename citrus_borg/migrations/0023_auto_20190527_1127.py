# Generated by Django 2.1.4 on 2019-05-27 18:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('citrus_borg', '0017_auto_20190308_0908'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalallowedeventsource',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='historicalallowedeventsource',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalallowedeventsource',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='historicalborgsite',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='historicalborgsite',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalborgsite',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='historicalknownbrokeringdevice',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='historicalknownbrokeringdevice',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalknownbrokeringdevice',
            name='updated_by',
        ),
        migrations.AlterModelOptions(
            name='borgsite',
            options={'verbose_name': 'Bot Site', 'verbose_name_plural': 'Bot Sites'},
        ),
        migrations.AlterModelOptions(
            name='borgsitenotseen',
            options={'ordering': ('-winlogbeathost__last_seen',), 'verbose_name': 'Bot Site', 'verbose_name_plural': 'Bot Sites not seen for a while'},
        ),
        migrations.AlterModelOptions(
            name='knownbrokeringdevicenotseen',
            options={'verbose_name': 'Citrix App Server', 'verbose_name_plural': 'Citrix App Servers not seen for a while'},
        ),
        migrations.AlterModelOptions(
            name='winlogbeathost',
            options={'verbose_name': 'Remote Monitoring Bot', 'verbose_name_plural': 'Remote Monitoring Bots'},
        ),
        migrations.AlterModelOptions(
            name='winlogbeathostnotseen',
            options={'verbose_name': 'Remote Monitoring Bot', 'verbose_name_plural': 'Remote Monitoring Bots not seen for a while'},
        ),
        migrations.AlterModelOptions(
            name='winlogevent',
            options={'verbose_name': 'Citrix Bot Windows Log Event', 'verbose_name_plural': 'Citrix Bot Windows Log Events'},
        ),
        migrations.DeleteModel(
            name='HistoricalAllowedEventSource',
        ),
        migrations.DeleteModel(
            name='HistoricalBorgSite',
        ),
        migrations.DeleteModel(
            name='HistoricalKnownBrokeringDevice',
        ),
    ]
