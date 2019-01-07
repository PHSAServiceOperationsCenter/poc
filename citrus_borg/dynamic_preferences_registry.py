"""
.. _dynamic_preferences_registry:

dynamic preferences for the citrus_borg app

:module:    citrus_borg.dynamic_preferences_registry

:copyright:

    Copyright 2019 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

:updated:    jan. 3, 2019

"""
from django.conf import settings
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.types import (
    BooleanPreference, StringPreference, DurationPreference, IntPreference,
)
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

# pylint: disable=E1101,C0103
#=========================================================================
# E1101: instance of '__proxy__' has no 'title' member caused by using .title()
# on returns from gettext_lazy()
#
# C0103: asr PEP8 module level variables are constants and should be upper-case
#=========================================================================


citrus_borg_common = Section(
    'citrusborgcommon', verbose_name=_('citrus borg common settings').title())

citrus_borg_events = Section(
    'citrusborgevents', verbose_name=_('citrus borg event settings').title())

citrus_borg_node = Section(
    'citrusborgnode', verbose_name=_('Citrus Borg Node settings').title())

citrus_borg_ux = Section(
    'citrusborgux',
    verbose_name=_('Citrus Borg User Experience settings').title())

citrus_borg_logon = Section(
    'citrusborglogon',
    verbose_name=_('Citrus Borg Citrix Logon settings').title())

# pylint: enable=C0103


@global_preferences_registry.register
class ServiceUser(StringPreference):
    """
    service or default user preference
    """
    section = citrus_borg_common
    name = 'service_user'
    default = settings.CITRUS_BORG_SERVICE_USER
    required = True
    verbose_name = _('citrus borg service user').title()
    help_text = format_html(
        "{}<br>{}",
        _('default django user instance for background server processes.'),
        _('will be created automatically if it does not exist already'))


@global_preferences_registry.register
class SendNoNews(BooleanPreference):
    """
    send empty alerts preference
    """
    section = citrus_borg_common
    name = 'send_no_news'
    default = settings.CITRUS_BORG_NO_NEWS_IS_GOOD_NEWS
    required = False
    verbose_name = _("do not send empty citrix alert emails").title()
    help_text = format_html(
        "{}<br>{}",
        _('by default the application sends alert emails even if there is no'
          ' alert.'),
        _('enable this setting to only send alert emails if alerts have'
          ' occurred'))


@global_preferences_registry.register
class DeadAfter(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_common
    name = 'dead_after'
    default = settings.CITRUS_BORG_IGNORE_EVENTS_OLDER_THAN
    required = True
    verbose_name = _('dead if not seen for more than').title()
    help_text = format_html(
        "{}<br>{}",
        _('report a site, bot, or session host as dead if events mentioning'),
        _('them have not been received for more than this time period'))


@global_preferences_registry.register
class IgnoreEvents(DurationPreference):
    """
    ignore events older than preference
    """
    section = citrus_borg_events
    name = 'ignore_events_older_than'
    default = settings.CITRUS_BORG_IGNORE_EVENTS_OLDER_THAN
    required = True
    verbose_name = _('ignore events created older than').title()
    help_text = _(
        'events older than this value will not be used for any analysis')


@global_preferences_registry.register
class ExpireEvents(DurationPreference):
    """
    expire events older than preference
    """
    section = citrus_borg_events
    name = 'expire_events_older_than'
    default = settings.CITRUS_BORG_EVENTS_EXPIRE_AFTER
    required = True
    verbose_name = _('mark events as expired if older than').title()
    help_text = _(
        'events older than this value will be marked as expired')


@global_preferences_registry.register
class DeleteExpireEvents(BooleanPreference):
    """
    delete expired eventss preference
    """
    section = citrus_borg_events
    name = 'delete_expired_events'
    default = settings.CITRUS_BORG_DELETE_EXPIRED
    required = False
    verbose_name = _('delete expired events').title()


@global_preferences_registry.register
class UxAlertThreshold(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_ux
    name = 'ux_alert_threshold'
    default = settings.CITRUS_BORG_UX_ALERT_THRESHOLD
    required = True
    verbose_name = _(
        'maximum acceptable response time for citrix events').title()
    help_text = format_html(
        "{}<br>{}",
        _('raise a user experience degraded alert if the response time for'),
        _('any monitored citrix event is higher than this value'))


@global_preferences_registry.register
class UxAlertInterval(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_ux
    name = 'ux_alert_interval'
    default = settings.CITRUS_BORG_UX_ALERT_INTERVAL
    required = True
    verbose_name = _('alert monitoring interval for citrix events').title()
    help_text = format_html(
        "{}<br>{}",
        _('measure the user experience response time for citrix events'),
        _('once per this time interval for every site/bot combination'))


@global_preferences_registry.register
class UxReportingPeriod(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_ux
    name = 'ux_reporting_period'
    default = settings.CITRUS_BORG_SITE_UX_REPORTING_PERIOD
    required = True
    verbose_name = _('user experience reporting period').title()
    help_text = format_html(
        "{}<br>{}",
        _('email a report with the citrix event response time averaged'),
        _('per hour for each site, bot comination over this time interval'))


@global_preferences_registry.register
class NodeForgottenAfter(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_node
    name = 'node_forgotten_after'
    default = settings.CITRUS_BORG_NOT_FORGOTTEN_UNTIL_AFTER
    required = True
    verbose_name = _('reporting period for dead nodes').title()
    help_text = format_html(
        "{}<br>{}",
        _('reports about dead bots, site, or session hosts are based'),
        _('on this period'))


@global_preferences_registry.register
class BotAlertAfter(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_node
    name = 'dead_bot_after'
    default = settings.CITRUS_BORG_DEAD_BOT_AFTER
    required = True
    verbose_name = _('bot not seen alert threshold').title()
    help_text = format_html(
        "{}<br>{}",
        _('raise an alert if a bot has not sent any events for a period'),
        _('longer than this time interval'))


@global_preferences_registry.register
class SiteAlertAfter(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_node
    name = 'dead_site_after'
    default = settings.CITRUS_BORG_DEAD_SITE_AFTER
    required = True
    verbose_name = _('site not seen alert threshold').title()
    help_text = format_html(
        "{}<br>{}",
        _('raise an alert if none of the bots on a site has sent any events'),
        _('for a period longer than this time interval'))


@global_preferences_registry.register
class SessionHostAlertAfter(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_node
    name = 'dead_session_host_after'
    default = settings.CITRUS_BORG_DEAD_BROKER_AFTER
    required = True
    verbose_name = _('session host not seen alert threshold').title()
    help_text = format_html(
        "{}<br>{}<br>{}<br>{}",
        _('raise an alert if a known session host has not served any Citrix'),
        _('requests for a period longer than this time interval.'),
        _('note that session hosts are owned by Cerner and these alerts are'),
        _('mostly informative in nature'))


@global_preferences_registry.register
class FailedLogonAlertInterval(DurationPreference):
    """
    reprot something as dead after preference
    """
    section = citrus_borg_logon
    name = 'logon_alert_after'
    default = settings.CITRUS_BORG_FAILED_LOGON_ALERT_INTERVAL
    required = True
    verbose_name = _('failed logons alert interval').title()
    help_text = format_html(
        "{}<br>{}",
        _('interval at which to verify sites and bots for failed logon'),
        _('events'))


@global_preferences_registry.register
class FailedLogonAlertThreshold(IntPreference):
    """
    failed logon events count threshold preference
    """
    section = citrus_borg_logon
    name = 'logon_alert_threshold'
    required = True
    default = settings.CITRUS_BORG_FAILED_LOGON_ALERT_THRESHOLD
    verbose_name = _('failed logon events count alert threshold').title()
    help_text = format_html(
        "{}<br>{}",
        _('how many times does a failed logon happen in a given interval'),
        _('before an alert is raised'))


@global_preferences_registry.register
class LogonReportsInterval(DurationPreference):
    """
    report interval for logon events preference
    """
    section = citrus_borg_logon
    name = 'logon_report_period'
    default = settings.CITRUS_BORG_FAILED_LOGONS_PERIOD
    required = True
    verbose_name = _('logon events reporting period').title()
    help_text = format_html(
        "{}<br>{}",
        _('logon reports are calculated, created, and sent over this'),
        _('time interval'))

# pylint: enable=E1101


def get_preference(key=None):
    """
    get the preference
    """
    preferences = global_preferences_registry.manager().load_from_db()
    try:
        return preferences.get(key)
    except Exception as error:
        raise error
