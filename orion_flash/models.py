"""
.. _models:

django models module for the orion_flash app

:module:    p_soc_auto.orion_flash.models

:copyright:

    Copyright 2018 - 2019 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

:updated:    Jan. 15, 2019

"""
import logging
import pendulum

from django.db import models
from django.utils.translation import gettext_lazy as _


LOG = logging.getLogger('orion_flash')


class SslAlertError(Exception):
    """
    custom exception wrapper for this module
    """


class BaseSslAlert(models.Model):
    """
    class for Orion custom alerts related to SSL certificates

    the alerts will show up in Orion when a query joining this table to an
    Orion entity (initially an Orion.Node) is defined in Orion as a custom
    alert

    our application is populating and maintaining this model regularly via
    celery tasks

    the Orion SQL queries joined to models inheriting from this model
    will each represent a specific alert definition

    periodically the Orion server is evaluating the alerts by executing the
    joined query which must filter on silenced = False.
    alerts can be silenced from the django admin by setting the silenced field
    to True

    the django admin link is present in the self_url field. it must be an
    absolute link and it must be always updated in the post_save event
    """
    orion_node_id = models.BigIntegerField(
        _('Orion Node Id'), db_index=True, blank=False, null=False,
        help_text=_(
            'this is the value in this field to'
            ' SQL join the Orion server database'))
    orion_node_port = models.BigIntegerField(
        _('Orion Node TCP Port'), db_index=True, blank=False, null=False)
    cert_url = models.URLField(
        _('SSL certificate URL'), blank=False, null=False)
    cert_subject = models.TextField(
        _('SSL certificate subject'), blank=False, null=False)
    first_raised_on = models.DateTimeField(
        _('alert first raised on'), db_index=True, auto_now_add=True,
        blank=False, null=False)
    last_raised_on = models.DateTimeField(
        _('alert last raised on'), db_index=True, auto_now=True,
        blank=False, null=False)
    silenced = models.BooleanField(
        _('silence this alert?'), db_index=True, default=False, null=False,
        blank=False,
        help_text=_('The Orion server will ignore this row when evaluating'
                    ' alert conditions. Note that this flag will be'
                    ' automatically reset every $configurable_interval'))
    alert_body = models.TextField(
        _('alert body'), blank=False, null=False)
    cert_issuer = models.TextField(
        _('SSL certificate issuing authority'), blank=False, null=False)
    cert_issuer_url = models.URLField(
        _('SSL certificate issuing authority URL'), blank=True, null=True)
    self_url = models.URLField(
        _('Custom SSL alert URL'), blank=True, null=True)
    md5 = models.CharField(
        _('primary key md5 fingerprint'), db_index=True,
        max_length=64, blank=False, null=False)
    not_before = models.DateTimeField(
        _('not valid before'), db_index=True, null=False, blank=False)
    not_after = models.DateTimeField(
        _('not valid after'), db_index=True, null=False, blank=False)

    def __str__(self):
        return self.cert_subject

    def set_attr(self, attr_name, attr_value):
        """
        we want to set self.has_expired (for example) but this is an
        abstract model and there are fields that are only defined in
        its children

        we don't know the name of the field and we don't know if the
        model has said field until we actually execute this and we also
        want to reuse this for more than one field

        """
        if hasattr(self, attr_name):
            setattr(self, attr_name, attr_value)

    @classmethod
    def create_or_update(cls, qs_row_as_dict):
        """
        create orion custom alert objects

        :arg qs_row_as_dict:

            an item from the return of
            :method:`<django.db.models.query.Queryset.values>`. we can
            accept that this method returns a ``list`` of ``dict`` therefore
            this argument can be treated as a ``dict``

        """

        def get_subject():
            return 'CN: {}, O: {}, C:{}'.format(
                qs_row_as_dict.get('common_name'),
                qs_row_as_dict.get('organization_name'),
                qs_row_as_dict.get('country_name')
            )

        def get_issuer():
            return 'CN: {}, O: {}, C:{}'.format(
                qs_row_as_dict.get('issuer__common_name'),
                qs_row_as_dict.get('issuer__organization_name'),
                qs_row_as_dict.get('issuer__country_name')
            )

        ssl_alert = cls.objects.filter(
            orion_node_id=qs_row_as_dict.get('orion_id'),
            orion_node_port=qs_row_as_dict.get('port__port'))

        if ssl_alert.exists():
            ssl_alert = ssl_alert.get()

            ssl_alert.silenced = False
            ssl_alert.alert_body = qs_row_as_dict.get('alert_body')
            ssl_alert.set_attr(
                'expires_in', qs_row_as_dict.get('expires_in_x_days'))
            ssl_alert.set_attr(
                'expires_in_lt',
                qs_row_as_dict.get('expires_in_less_than'))
            ssl_alert.set_attr(
                'has_expired',
                qs_row_as_dict.get('has_expired_x_days_ago'))
            ssl_alert.set_attr(
                'invalid_for',
                qs_row_as_dict.get('will_become_valid_in_x_days'))

            if ssl_alert.md5 == qs_row_as_dict.get('pk_md5'):
                msg = 'updated alert for unchanged SSL certificate {}'.format(
                    ssl_alert.cert_subject)

            else:
                ssl_alert.cert_subject = get_subject()
                ssl_alert.ssl_cert_issuer = get_issuer()
                ssl_alert.cert_issuer_url = qs_row_as_dict.get('url_issuer')
                ssl_alert.md5 = qs_row_as_dict.get('pk_md5')
                ssl_alert.not_before = qs_row_as_dict.get('not_before')
                ssl_alert.not_after = qs_row_as_dict.get('not_after')
                msg = 'updated alert and information for SSL certificate {}'.\
                    format(ssl_alert.cert_subject)

        else:
            ssl_alert = cls(
                orion_node_id=qs_row_as_dict.get('orion_id'),
                orion_node_port=qs_row_as_dict.get('port__port'),
                cert_url=qs_row_as_dict.get('url'),
                cert_subject=get_subject(),
                cert_issuer=get_issuer(),
                cert_issuer_url=qs_row_as_dict.get('url_issuer'),
                md5=qs_row_as_dict.get('pk_md5'),
                alert_body=qs_row_as_dict.get('alert_body'),
                not_before=qs_row_as_dict.get('not_before'),
                not_after=qs_row_as_dict.get('not_after')
            )
            ssl_alert.set_attr(
                'cert_is_trusted', qs_row_as_dict.get('issuer__is_trusted'))
            ssl_alert.set_attr(
                'expires_in', qs_row_as_dict.get('expires_in_x_days'))
            ssl_alert.set_attr(
                'expires_in_lt', qs_row_as_dict.get('expires_in_less_than'))
            ssl_alert.set_attr(
                'has_expired', qs_row_as_dict.get('has_expired_x_days_ago'))
            ssl_alert.set_attr(
                'invalid_for',
                qs_row_as_dict.get('will_become_valid_in_x_days'))

            msg = 'created alert for SSL certificate {}'.format(
                ssl_alert.cert_subject)

        try:
            ssl_alert.save()
        except Exception as err:
            raise SslAlertError from err

        return msg

    class Meta:
        abstract = True


class UntrustedSslAlert(BaseSslAlert, models.Model):
    """
    model to join to Orion.Node for alerts regarding untrusted
    SSL certificates

    the filter used in the Orion alert definition is:
    where cert_is_trusted = False and silenced = False

    the model is populated via celery tasks by periodically calling
    :function:`<ssl_cert_tracker.lib.is_not_trusted>` and iterating through
    the queryset.

    the model needs to also be trimmed. use a celery task to iterate
    through each instance. use the node:port combination to extract the
    corresponding row from :class:`<ssl_cert_tracker.models.SslCertificate>`

        *    if a corresponding row is found, next

        *    otherwise, the certificate doesn't exist anymore so there is no
             alert, delete the alert row
    """
    qs_fields = [
        'orion_id', 'port__port', 'common_name', 'organization_name',
        'country_name', 'issuer__common_name', 'issuer__organization_name',
        'issuer__country_name', 'url', 'not_before', 'not_after', 'pk_md5',
        'alert_body',
        'issuer__is_trusted', 'url_issuer',
    ]

    cert_is_trusted = models.BooleanField(
        _('is trusted'), db_index=True, null=False, blank=False)

    def __str__(self):
        return 'untrusted SSL certificate {}'.format(self.cert_subject)

    class Meta:
        verbose_name = _('Custom Orion Alert for untrusted SSL certificates')
        verbose_name_plural = _(
            'Custom Orion Alerts for untrusted SSL certificates')


class ExpiresSoonSslAlert(BaseSslAlert, models.Model):
    """
    model to join to Orion.Node for alerts regarding SSL certificates that
    will expire in less than a given period of time

    this model is populated via celery tasks periodically calling
    :function:`<ssl_cert_tracker.lib.expires_in>` with various values for the
    lt_days argument and iterating through the queryset returned by said
    function.

    one must define a different Orion alert for each desired lt_days value
    and the filter used in the joined query must match that value.
    lt_days is mapped to the field named 'expires_in_less_than'.

    the model needs to be trimmed. see previous model for ideas
    """
    qs_fields = [
        'orion_id', 'port__port', 'common_name', 'organization_name',
        'country_name', 'issuer__common_name', 'issuer__organization_name',
        'issuer__country_name', 'url', 'not_before', 'not_after', 'pk_md5',
        'alert_body',
        'expires_in_x_days', 'expires_in_less_than', 'url_issuer',
    ]

    expires_in = models.BigIntegerField(
        _('expires in'), db_index=True, blank=False, null=False)
    expires_in_lt = models.BigIntegerField(
        _('expires in less than'), db_index=True, blank=False, null=False)

    def __str__(self):
        return 'SSL certificate {} will expire in {} days'.format(
            self.cert_subject, self.expires_in)

    class Meta:
        verbose_name = _('SSL Certificates Expiration Warning')
        verbose_name_plural = _('SSL Certificates Expiration Warnings')


class ExpiredSslAlert(BaseSslAlert, models.Model):
    """
    model to join to Orion.Node for alerts about expires SSL certificates

    see previous model(s) for ideas
    """
    qs_fields = [
        'orion_id', 'port__port', 'common_name', 'organization_name',
        'country_name', 'issuer__common_name', 'issuer__organization_name',
        'issuer__country_name', 'url', 'not_before', 'not_after', 'pk_md5',
        'alert_body',
        'has_expired_x_days_ago', 'url_issuer',
    ]

    has_expired = models.BigIntegerField(
        _('has expired'), db_index=True, blank=False, null=False)

    def __str__(self):
        return 'SSL certificate {} has expired {} days ago'.format(
            self.cert_subject, self.has_expired)

    class Meta:
        verbose_name = _('Expired SSL Certificates Alert')
        verbose_name_plural = _('Expired SSL Certificates Alerts')


class InvalidSslAlert(BaseSslAlert, models.Model):
    """
    model to join to Orion.Node for alerts about SSL certificates that are
    not yet valid

    see previous model(s) for ideas
    """
    qs_fields = [
        'orion_id', 'port__port', 'common_name', 'organization_name',
        'country_name', 'issuer__common_name', 'issuer__organization_name',
        'issuer__country_name', 'url', 'not_before', 'not_after', 'pk_md5',
        'alert_body',
        'will_become_valid_in_x_days', 'url_issuer',
    ]

    invalid_for = models.BigIntegerField(
        _('will become valid in'), db_index=True, blank=False, null=False)

    def __str__(self):
        return 'SSL certificate {} will become valid in {} days'.format(
            self.cert_subject, self.invalid_for)

    class Meta:
        verbose_name = _('Not Yet Valid SSL Certificates Alert')
        verbose_name_plural = _('Not Yet Valid SSL Certificates Alert')


class BaseCitrusBorgAlert(models.Model):
    """
    common fields, attributes, methods for custom alerts related to Citrix bots
    """
    orion_node_id = models.BigIntegerField(
        _('Orion Node Id'), db_index=True, blank=False, null=False,
        help_text=_('this is the value in this field to'
                    ' SQL join the Orion server database'))
    first_raised_on = models.DateTimeField(
        _('alert first raised on'), db_index=True, auto_now_add=True,
        blank=False, null=False)
    last_raised_on = models.DateTimeField(
        _('alert last raised on'), db_index=True, auto_now=True,
        blank=False, null=False)
    silenced = models.BooleanField(
        _('silence this alert?'), db_index=True, default=False, null=False,
        blank=False,
        help_text=_('The Orion server will ignore this row when evaluating'
                    ' alert conditions. Note that this flag will be'
                    ' automatically reset every $configurable_interval'))
    alert_body = models.TextField(
        _('alert body'), blank=False, null=False)
    bot_url = models.URLField(
        _('Citrix bot URL'), blank=False, null=False)
    events_url = models.URLField(
        _('ControlUp windows log events URL'), blank=False, null=False)
    self_url = models.URLField(
        _('SSL certificate URL'), blank=True, null=True)
    host_name = models.CharField(
        _('host name'), max_length=63, db_index=True, unique=True,
        blank=False, null=False)
    site = models.CharField(
        _('host name'), max_length=64, db_index=True,
        blank=False, null=False)
    measured_now = models.DateTimeField(
        _('measured from'),
        help_text=_('the definition of now. normally it is now() but it can'
                    ' be any moment in time for which we have data'))
    measured_over_mins = models.BigIntegerField(
        _('not seen threshold measured in minutes'), db_index=True,
        help_text=_(
            'use this field to compare if threshold is specified in minutes'))
    measured_over_hours = models.BigIntegerField(
        _('not seen threshold measured in hours'), db_index=True,
        help_text=_(
            'use this field to compare if threshold is specified in hours'))
    measured_over_days = models.BigIntegerField(
        _('not seen threshold measured in days'), db_index=True,
        help_text=_(
            'use this field to compare if threshold is specified in days'))

    def __str__(self):
        return '{}: {}'.format(self.host_name, self.alert_body)

    def set_attr(self, attr_name, attr_value):
        """
        we want to set self.has_expired (for example) but this is an
        abstract model and there are fields that are only defined in
        its children

        we don't know the name of the field and we don't know if the
        model has said field until we actually execute this and we also
        want to reuse this for more than one field

        """
        if hasattr(self, attr_name):
            setattr(self, attr_name, attr_value)

    @classmethod
    def create_or_update(cls, qs_row_as_dict):
        """
        create orion custom alert objects

        :arg qs_row_as_dict:

            an item from the return of
            :method:`<django.db.models.query.Queryset.values>`. we can
            accept that this method returns a ``list`` of ``dict`` therefore
            this argument can be treated as a ``dict``

        """
        def duration(duration):
            """
            helper function to create a pendulum duration object from
            a django timezone.timedelta object
            """
            return pendulum.duration(days=duration.days,
                                     seconds=duration.seconds,
                                     microseconds=duration.microseconds)

        borg_alert = cls.objects.filter(
            host_name__iequals=qs_row_as_dict.get('host_name'))

        if borg_alert.exists():
            borg_alert = borg_alert.get()

        else:
            borg_alert = cls(orion_node_id=qs_row_as_dict.get('host_name'))

        borg_alert.silenced = False
        borg_alert.site = qs_row_as_dict.get('site__site')
        borg_alert.bot_url = qs_row_as_dict.get('url')
        borg_alert.events_url = qs_row_as_dict.get('details_url')
        borg_alert.orion_node_id = qs_row_as_dict.get('orion_id')
        borg_alert.measured_now = qs_row_as_dict.get('measured_now')
        borg_alert.measured_over_days = duration(
            qs_row_as_dict.get('measured_over')).in_days()
        borg_alert.measured_over_hours = duration(
            qs_row_as_dict.get('measured_over')).in_hours()
        borg_alert.measured_over_mins = duration(
            qs_row_as_dict.get('measured_over')).in_minutes()

        borg_alert.set_attr('last_seen', qs_row_as_dict.get('last_seen'))
        borg_alert.set_attr('not_seen_for',
                            pendulum.now(tz='UTC').diff_for_humans(
                                qs_row_as_dict.get('last_seen')
                            ))

        borg_alert.set_attr(
            'failed_events_count', qs_row_as_dict.get('failed_events'))
        borg_alert.set_attr(
            'failed_events_threshold',
            qs_row_as_dict.get('failed_threshold'))

        borg_alert.alert_body = borg_alert.set_alert_body()

    class Meta:
        abstract = True


class DeadCitrusBotAlert(BaseCitrusBorgAlert, models.Model):
    """
    alerts about bots that have not been seen for a while

    we cannot usse duration fields here, we need to use floats and/or ints
    because we need to feed comparions into the sql query that defines the
    alarm

    btw, MSSQL and probably most databases do not support a native timedelta
    data type, it is the driver that handles the conversions

    we may have to use pandas.Timedelta.round() to convert to hours and/or
    minutes
    """
    qs_fields = ['orion_id', 'url', 'details_url', 'host_name',
                 'last_seen', 'measured_over', 'site__site', 'measured_now', ]

    last_seen = models.DateTimeField(
        _('last seen'),
        help_text=_('last seen as shown in WinlogbeatHost'))
    not_seen_for = models.CharField(
        _('not seen for'), max_length=64, blank=True, null=True,
        help_text='the diference between now and last_seen converted to'
        ' a suitable time unit')

    def set_alert_body(self):
        """
        set the alert_body
        """
        alert_template = (
            'Citrix bot %s at %s has not sent ControlUp logon'
            ' events for more than {measured_over} {units}') % (self.host_name,
                                                                self.site)

        if self.measured_over_days > 0:
            return alert_template.format(
                units='days', measured_over=self.measured_over_days)

        if self.measured_over_hours > 0:
            return alert_template.format(
                units='hours', measured_over=self.measured_over_hours)

        return alert_template.format(
            units='minutes', measured_over=self.measured_over_mins)


class CitrusBorgLoginAlert(BaseCitrusBorgAlert, models.Model):
    """
    alerts about citrix logon failures on bots
    """
    qs_fields = ['orion_id', 'url', 'details_url', 'host_name',
                 'measured_over', 'site__site', 'measured_now',
                 'failed_events', 'failed_threshold', ]

    failed_events_count = models.BigIntegerField(
        _('failed event count'), blank=False, null=False)
    failed_events_threshold = models.BigIntegerField(
        _('failed event count threshold'), db_index=True, blank=False,
        null=False,
        help_text=_('trigger failed logon alerts against this field'))

    def set_alert_body(self):
        """
        set the alert body
        """
        alert_template = (
            'Citrix bot %s at %s has had at least %s failed ControlUp'
            ' logon  events over the last {measured_over} {units}'
        ) % (self.host_name, self.site, self.failed_events_count)

        if self.measured_over_days > 0:
            return alert_template.format(
                units='days', measured_over=self.measured_over_days)

        if self.measured_over_hours > 0:
            return alert_template.format(
                units='hours', measured_over=self.measured_over_hours)

        return alert_template.format(
            units='minutes', measured_over=self.measured_over_mins)


class CitrusBorgUxAlert(BaseCitrusBorgAlert, models.Model):
    """
    alerts about Citrix response times
    """
    avg_response_time = models.DurationField()
    avg_response_time_threshold = models.DurationField()
