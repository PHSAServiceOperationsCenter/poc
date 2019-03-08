"""
.. _models:

django models for the citrus_borg app

:module:    citrus_borg.models

:copyright:

    Copyright 2018 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

:updated:    nov. 19, 2018

"""
import socket
import uuid

from django.conf import settings
from django.db import models
from django.db.models.deletion import SET_NULL
from django.utils.timezone import now, timedelta
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from p_soc_auto_base.models import BaseModel
from orion_integration.orion import OrionClient


def get_uuid():
    """
    provide default value for UUID fields

    :returns: an instance of :class:`<uuid.UUID>` that ca  be used as a
              unique identifier
    """
    return uuid.uuid4()

# pylint: disable=too-few-public-methods,no-self-use


class BorgSiteNotSeenManager(models.Manager):
    """
    custom manager for :class:`<BorgSite>`
    """

    def get_queryset(self):
        """
        override the get_queryset method
        """
        return BorgSite.objects.\
            exclude(winlogbeathost__last_seen__gt=now() -
                    settings.CITRUS_BORG_NOT_FORGOTTEN_UNTIL_AFTER)

# pylint: enable=too-few-public-methods,no-self-use


class BorgSite(BaseModel, models.Model):
    """
    sites with with citrix bots
    """
    site = models.CharField(
        _('site name'), max_length=64, db_index=True, unique=True,
        blank=False, null=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.site

    class Meta:
        app_label = 'citrus_borg'
        verbose_name = _('Citrix Bot Site')
        verbose_name_plural = _('Citrix Bot Sites')


class BorgSiteNotSeen(BorgSite):
    objects = BorgSiteNotSeenManager()

    class Meta:
        proxy = True
        ordering = ('-winlogbeathost__last_seen',)
        verbose_name = _('Citrix Bot Site')
        verbose_name_plural = _(
            'Citrix Bot Sites not seen for at least 72 hours')


class WinlogbeatHostNotSeenManager(models.Manager):
    def get_queryset(self):
        return WinlogbeatHost.objects.\
            exclude(last_seen__gt=now() -
                    settings.CITRUS_BORG_NOT_FORGOTTEN_UNTIL_AFTER)


class WinlogbeatHost(BaseModel, models.Model):
    """
    hosts where the winlogbeat daemon is collecting windows events
    """
    host_name = models.CharField(
        _('host name'), max_length=63, db_index=True, unique=True,
        blank=False, null=False)
    ip_address = models.GenericIPAddressField(
        _('IP address'), protocol='IPv4', blank=True, null=True)
    last_seen = models.DateTimeField(
        _('last seen'), db_index=True, blank=False, null=False)
    site = models.ForeignKey(
        BorgSite, db_index=True, blank=True, null=True,
        on_delete=models.SET_NULL)
    orion_id = models.BigIntegerField(
        _('Orion Object Id'), db_index=False, unique=False, blank=True,
        null=True, default=0,
        help_text=_(
            'Use the value in this field to query the Orion server'))

    @property
    def resolved_fqdn(self):
        return socket.getfqdn(self.ip_address) if self.ip_address else None

    def get_orion_id(self):
        """
        use the resolved_fqdn or the ip address to ask the orion server
        for the orion id

        the normal way to call this method is to wrap it a celery task.
        invoke it from the post_save event.

        post_save is triggered from :method:`<get_or_create_from_borg>` which
        is invoked by celery every tiume an winlogbeat sends an event for this
        host. we don't need to worry about pre-populating this on our own

        see this to avoid the infinite save loop in post_save
        http://www.re-cycledair.com/saving-within-a-post_save-signal-in-django

        need to rethink this big time:
        we are grabbing stuff from orion in a model.save
        (actually model.signals.post_save) which means that we are
        chaining a lot fo async calls

        maybe it is a better idea to have this running in a completely
        separate group of tasks with each task responsible for updating
        one winloghost instance on it's own.
        no more post_save interactions with all the recurring depth mess

        calliong this method from a celery task does is not idempotent,
        or at least it puts too many balls in the air

        """
        def save_in_post_save():
            self.orion_id = orion_id
            models.signals.post_save.disconnect(self.save, self._meta.model)
            self.save()
            models.signals.post_save.connect(self.save, self._meta.model)

        orion_query = (
            'SELECT NodeID FROM Orion.Nodes(nolock=true) '
            'WHERE %s=%s')

        if not self.enabled:
            # it's disabled, we don't care so go away
            return

        if self.resolved_fqdn is None and self.ip_address is None:
            # there is no way to identity the node in orion

            # TODO: this is an error condition, must integrate with
            # https://trello.com/c/1Aadwukn
            return

        if self.resolved_fqdn:
            orion_query_by_dns = orion_query % ("ToLower('DNS')",
                                                self.resolved_fqdn.lower())
            orion_id = OrionClient.query(
                orion_query=orion_query_by_dns).get('NodeID')
            if orion_id:
                save_in_post_save()
                return

        orion_query_by_ip = orion_query % ('IPAddress', self.ip_address)
        orion_id = OrionClient.query(
            orion_query=orion_query_by_ip).get('NodeID')

        if orion_id:
            save_in_post_save()

        return

    def __str__(self):
        return '%s (%s)' % (self.host_name, self.ip_address)

    @classmethod
    def get_or_create_from_borg(cls, borg):
        """
        get the host object based on host information in the windows event

        if the host object doesn't exist, create it first

        :arg borg: the namedtuple containing the windows event data

        :returns: a host object
        """
        winloghost = cls.objects.filter(
            host_name__iexact=borg.source_host.host_name)

        if winloghost.exists():
            winloghost = winloghost.get()
            winloghost.last_seen = now()
        else:
            user = cls.get_or_create_user(settings.CITRUS_BORG_SERVICE_USER)
            winloghost = cls(
                host_name=borg.source_host.host_name, last_seen=now(),
                ip_address=borg.source_host.ip_address, created_by=user,
                updated_by=user)

        winloghost.save()
        return winloghost

    class Meta:
        verbose_name = _('Citrix Bot')
        verbose_name_plural = _('Citrix Bots')


class WinlogbeatHostNotSeen(WinlogbeatHost):
    objects = WinlogbeatHostNotSeenManager()

    class Meta:
        proxy = True
        verbose_name = _('Citrix Bot')
        verbose_name_plural = _('Citrix Bots not seen for at least 72 hours')


class AllowedEventSource(BaseModel, models.Model):
    """
    only save events originating from specific Log_name and source_name
    combinations
    """
    source_name = models.CharField(
        _('source name'), max_length=253, db_index=True, blank=False,
        null=False, unique=True, help_text=_(
            'the equivalent of filtering by -ProviderName in Get-WinEvent:'
            ' the application will only capture events generated by'
            ' providers listed in this model'))
    history = HistoricalRecords()

    def __str__(self):
        return self.source_name

    class Meta:
        verbose_name = _('Allowed Event Source')
        verbose_name_plural = _('Allowed Event Sources')


class WindowsLog(BaseModel, models.Model):
    """
    windows log names lookup
    """
    log_name = models.CharField(
        _('Log Name'), max_length=64, unique=True, db_index=True, blank=False,
        null=False)

    def __str__(self):
        return self.log_name

    class Meta:
        verbose_name = _('Supported Windows Log')
        verbose_name_plural = _('Supported Windows Logs')


class KnownBrokeringDeviceNotSeenManager(models.Manager):
    def get_queryset(self):
        return KnownBrokeringDevice.objects.\
            exclude(last_seen__gt=now() -
                    settings.CITRUS_BORG_NOT_FORGOTTEN_UNTIL_AFTER)


class KnownBrokeringDevice(BaseModel, models.Model):
    """
    keep a list of brokers returned by the logon simulator
    """
    broker_name = models.CharField(
        _('server name'), max_length=15, unique=True, db_index=True,
        blank=False, null=False, help_text=_(
            'the name of a Citrix session server that has serviced at least'
            ' one request')
    )
    last_seen = models.DateTimeField(
        _('last seen'), db_index=True, blank=False, null=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.broker_name

    @classmethod
    def get_or_create_from_borg(cls, borg):
        """
        get the broker object based on host information in the windows event

        if the broker object doesn't exist, create it first

        :arg borg: the namedtuple containing the windows event data

        :returns: a host object
        """
        if borg.borg_message.broker is None:
            return None

        broker = cls.objects.filter(
            broker_name__iexact=borg.borg_message.broker)

        if broker.exists():
            broker = broker.get()
            broker.last_seen = now()
        else:
            user = cls.get_or_create_user(settings.CITRUS_BORG_SERVICE_USER)
            broker = cls(
                broker_name=borg.borg_message.broker, created_by=user,
                updated_by=user, last_seen=now())

        broker.save()
        return broker

    class Meta:
        verbose_name = _('Citrix App Server')
        verbose_name_plural = _('Citrix App Servers')


class KnownBrokeringDeviceNotSeen(KnownBrokeringDevice):
    objects = KnownBrokeringDeviceNotSeenManager()

    class Meta:
        proxy = True
        verbose_name = _('Citrix App Server')
        verbose_name_plural = _(
            'Citrix App Servers not seen for at least 24 hours')


class WinlogEvent(BaseModel, models.Model):
    """
    windows logs events
    """
    uuid = models.UUIDField(
        _('UUID'), unique=True, db_index=True, blank=False, null=False,
        default=get_uuid)
    source_host = models.ForeignKey(
        WinlogbeatHost, db_index=True, blank=False, null=False,
        on_delete=models.PROTECT, verbose_name=_('Event Source Host'))
    record_number = models.BigIntegerField(
        _('Record Number'), db_index=True, blank=False, null=False,
        help_text=_('event record external identifier'))
    event_source = models.ForeignKey(
        AllowedEventSource, db_index=True, blank=False, null=False,
        on_delete=models.PROTECT, verbose_name=_('Event Provider'))
    windows_log = models.ForeignKey(
        WindowsLog, db_index=True, blank=False, null=False,
        on_delete=models.PROTECT, verbose_name=_('Windows Log'))
    event_state = models.CharField(
        _('Status'), max_length=32, db_index=True, blank=False, null=False,
        default='TBD', help_text=_(
            'Status of the Citrix application logon request'))
    xml_broker = models.ForeignKey(
        KnownBrokeringDevice, db_index=True, blank=True, null=True,
        on_delete=SET_NULL, verbose_name=_('XML Broker'),
        help_text=_(
            'The Citrix XML Broker that successfully serviced this request'))
    event_test_result = models.NullBooleanField(_('Test Result'))
    storefront_connection_duration = models.DurationField(
        _('Storefront connection time'), db_index=True, blank=True, null=True)
    receiver_startup_duration = models.DurationField(
        _('receiver startup time'), db_index=True, blank=True, null=True)
    connection_achieved_duration = models.DurationField(
        _('Connection time'), db_index=True, blank=True, null=True)
    logon_achieved_duration = models.DurationField(
        _('Logon time'), db_index=True, blank=True, null=True)
    logoff_achieved_duration = models.DurationField(
        _('Logoff time'), db_index=True, blank=True, null=True)
    failure_reason = models.TextField(
        _('Failure Reason'), blank=True, null=True)
    failure_details = models.TextField(
        _('Failure Details'), blank=True, null=True)
    raw_message = models.TextField(
        _('Raw Message'), blank=True, null=True,
        help_text=_('the application cannot process this message'))
    is_expired = models.BooleanField(
        _('event has expired'), db_index=True, blank=False, null=False,
        default=False)

    def __str__(self):
        return str(self.uuid)
