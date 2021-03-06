# Generated by Django 2.2.3 on 2019-08-19 18:59

from django.conf import settings
from django.contrib.auth.models import User
from django.db import migrations
from django.utils import dateparse


def create_fake_site_bot(apps, schema_editor):

    user = User.objects.filter(username=settings.CITRUS_BORG_SERVICE_USER)
    if user.exists():
        user = user.get()
    else:
        user = User.objects.create_user(settings.CITRUS_BORG_SERVICE_USER)

    Site = apps.get_model('citrus_borg', 'BorgSite')
    Borg = apps.get_model('citrus_borg', 'WinlogbeatHost')
    ExchangeConfiguration = apps.get_model('mail_collector',
                                           'ExchangeConfiguration')

    sites_and_bots = [
        {'site': 'site.not.exist',
         'notes': (
             'fake site to be used when an exchange bot is first'
             ' seen by the system'),
         'enabled': False,
         'bots': [{'host_name': 'host.not.exist',
                   'notes': (
                       'fake host to be used when retrieving the exchange'
                       ' configuration for an exchange bot not known to the'
                       ' system'),
                   'exchange_client_config':
                   ExchangeConfiguration.objects.filter(is_default=True).get(),
                   'excgh_last_seen':
                   dateparse.parse_datetime('1970-01-01T00:00:00+00'),
                   'enabled': False}, ], },
    ]

    for _site in sites_and_bots:
        site = Site.objects.filter(site__iexact=_site['site'])
        if site.exists():
            site = site.get()
        else:
            site = Site(site=_site.get('site'), notes=_site.get('notes'),
                        created_by_id=user.id, updated_by_id=user.id,
                        enabled=_site.get('enabled'))
            site.save()
        for _bot in _site['bots']:
            bot = Borg.objects.filter(host_name__iexact=_bot['host_name'])
            if bot.exists():
                bot = bot.get()
            else:
                bot = Borg(
                    host_name=_bot['host_name'],
                    excgh_last_seen=_bot.get('excgh_last_seen'),
                    created_by_id=user.id, updated_by_id=user.id)

            bot.site = site
            bot.notes = _bot.get('notes')
            bot.enabled = _bot.get('enabled')
            bot.exchange_client_config = _bot.get('exchange_client_config')

            bot.save()


class Migration(migrations.Migration):

    dependencies = [
        ('citrus_borg', '0027_auto_20190819_1308'),
    ]

    operations = [
        migrations.RunPython(
            create_fake_site_bot, reverse_code=migrations.RunPython.noop)
    ]
