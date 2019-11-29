"""
ldap_probe.models
-----------------

This module contains the :class:`django.db.models.Model` models for the
:ref:`Domain Controllers Monitoring Application`.

:copyright:

    Copyright 2018 - 2019 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

:updated:    Nov. 27, 2019

"""
import logging
import socket

from django.db import models
from django.conf import settings
from django.core import validators
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from citrus_borg.dynamic_preferences_registry import get_preference
from p_soc_auto_base.models import BaseModel, BaseModelWithDefaultInstance
from p_soc_auto_base.utils import get_uuid, get_absolute_admin_change_url


LOGGER = logging.getLogger('ldap_probe_log')


def _get_default_ldap_search_base():
    """
    get the default value for the :attr:`LDAPBindCred.ldap_search_base`
    attribute
    """
    return get_preference('ldapprobe__search_dn_default')

# pylint: disable=too-few-public-methods


class LdapProbeLogFullBindManager(models.Manager):
    """
    custom :class:`django.db.models.Manager` used by the
    :class:`LdapProbeLogFullBind` model

    We have observed that the default set of `Windows` domain credentials
    will allow full LDAP binds for a limited number of `AD` controllers.
    By design LDAP probe data collected from these `AD` controllers will
    present with :attr:`LdapProbeLog.elapsed_bind` values that are not
    null (`None` in `Python` speak).
    """

    def get_queryset(self):  # pylint: disable=no-self-use
        """
        override :meth:`django.db.models.Manager.get_queryset`

        See `Modifying a manager's initial QuerySet
        <https://docs.djangoproject.com/en/2.2/topics/db/managers/#modifying-a-manager-s-initial-queryset>`__
        in the `Django` docs.

        :returns: a :class:`django.db.models.query.QuerySet` with the
            :class:`LdapProbeLog` instances that contain timing data for
            `LDAP` full bind operations

        """
        return LdapProbeLog.objects.filter(elapsed_bind__isnull=False)


class LdapProbeLogAnonBindManager(models.Manager):
    """
    custom :class:`django.db.models.Manager` used by the
    :class:`LdapProbeLogFullBind` model

    We have observed that the default set of `Windows` domain credentials
    will not allow full LDAP binds (see :class:`LdapProbeLogFullBindManager`)
    for most of `AD` controllers.
    By design LDAP probe data collected from these `AD` controllers will
    present with :attr:`LdapProbeLog.elapsed_anon_bind` values that are not
    null (`None` in `Python` speak).

    """

    def get_queryset(self):  # pylint: disable=no-self-use
        """
        override :meth:`django.db.models.Manager.get_queryset`

        See `Modifying a manager's initial QuerySet
        <https://docs.djangoproject.com/en/2.2/topics/db/managers/#modifying-a-manager-s-initial-queryset>`__
        in the `Django` docs.

        :returns: a :class:`django.db.models.query.QuerySet` with the
            :class:`LdapProbeLog` instances that contain timing data for
            `LDAP` anonymous bind operations

        """
        return LdapProbeLog.objects.filter(elapsed_anon_bind__isnull=False)


class LdapProbeLogFailedManager(models.Manager):
    """
    custom :class:`django.db.models.Manager` used by the
    :class:`LdapProbeLogFailed` model

    """

    def get_queryset(self):  # pylint: disable=no-self-use
        """
        override :meth:`django.db.models.Manager.get_queryset`

        See `Modifying a manager's initial QuerySet
        <https://docs.djangoproject.com/en/2.2/topics/db/managers/#modifying-a-manager-s-initial-queryset>`__
        in the `Django` docs.

        :returns: a :class:`django.db.models.query.QuerySet` with the
            :class:`LdapProbeLog` failed instances

        """
        return LdapProbeLog.objects.filter(failed=True)

# pylint: enable=too-few-public-methods


class LDAPBindCred(BaseModelWithDefaultInstance, models.Model):
    """
    :class:`django.db.models.Model` class used for storing credentials used
    for probing `Windows` domain controllers

    `LDAP Bind Credentials Set fields
    <../../../admin/doc/models/ldap_probe.ldapbindcred>`__
    """
    domain = models.CharField(
        _('windows domain'),
        max_length=15, db_index=True, blank=False, null=False,
        validators=[validators.validate_slug])
    username = models.CharField(
        _('domain username'),
        max_length=64, db_index=True, blank=False, null=False,
        validators=[validators.validate_slug])
    password = models.CharField(
        _('password'), max_length=64, blank=False, null=False)
    ldap_search_base = models.CharField(
        _('DN search base'), max_length=128, blank=False, null=False,
        default=_get_default_ldap_search_base)

    def __str__(self):
        return '%s\\%s' % (self.domain, self.username)

    class Meta:
        app_label = 'ldap_probe'
        constraints = [models.UniqueConstraint(
            fields=['domain', 'username'], name='unique_account')]
        indexes = [models.Index(fields=['domain', 'username'])]
        verbose_name = _('LDAP Bind Credentials Set')
        verbose_name_plural = _('LDAP Bind Credentials Sets')


class BaseADNode(BaseModel, models.Model):
    """
    `Django abastract model
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#abstract-base-classes>`__
    for storing information about `Windows` domain controller hosts
    """
    ldap_bind_cred = models.ForeignKey(
        'ldap_probe.LDAPBindCred', db_index=True, blank=False, null=False,
        default=LDAPBindCred.get_default, on_delete=models.PROTECT,
        verbose_name=_('LDAP Bind Credentials'))

    def get_node(self):  # pylint: disable=inconsistent-return-statements
        """
        get node network information in either `FQDN` or `IP` address format

        We need this function mostly for retrieving node address information
        from `Orion` nodes. `Orion` nodes are guaranteed to have an `IP`
        address but sometimes they don't have a valid `FQDN`.
        """
        if hasattr(self, 'node_dns'):
            return getattr(self, 'node_dns')

        if hasattr(self, 'node'):
            node = getattr(self, 'node')
            if node.node_dns:
                return node.node_dns
            return node.node_caption

    class Meta:
        abstract = True


class OrionADNode(BaseADNode, models.Model):
    """
    :class:`django.db.models.Model` class used for storing DNS information
    about `Windows` domain controller hosts defined on the `Orion`
    server

    `Domain Controller from Orion fields
    <../../../admin/doc/models/ldap_probe.orionnode>`__
    """
    node = models.OneToOneField(
        'orion_integration.OrionDomainControllerNode', db_index=True,
        blank=False, null=False, on_delete=models.CASCADE,
        verbose_name=_('Orion Node for Domain Controller'))

    def __str__(self):
        if self.node.node_dns:
            return self.node.node_dns

        return self.node.node_caption

    @property
    @mark_safe
    def orion_admin_url(self):
        """
        instance property containing the `URL` to the `Django admin` change
        form for this `AD` controller
        """
        return '<a href="%s">%s</>' % (reverse(
            'admin:orion_integration_orionnode_change', args=(self.node.id,)
        ), self.node.node_caption)

    @property
    @mark_safe
    def orion_url(self):
        """
        instance property containing the `URL` for the `Orion` node
        associated with this `AD` controller
        """
        return '<a href="%s%s">%s</a>' % (
            get_preference('orionserverconn__orion_server_url'),
            self.node.details_url, self.get_node())

    class Meta:
        app_label = 'ldap_probe'
        verbose_name = _('Domain Controller from Orion')
        verbose_name_plural = _('Domain Controllers from Orion')
        ordering = ('node__node_caption', )


class NonOrionADNode(BaseADNode, models.Model):
    """
    :class:`django.db.models.Model` class used for storing DNS information
    about `Windows` domain controller hosts not available on the `Orion`
    server

    `Domain Controller not present in Orion fields
    <../../../admin/doc/models/ldap_probe.nonorionnode>`__
    """
    node_dns = models.CharField(
        _('Fully Qualified Domain Name (FQDN)'), max_length=255,
        db_index=True, unique=True, blank=False, null=False,
        help_text=_(
            'The FQDN of the domain controller host. It must respect the'
            ' rules specified in'
            ' `RFC1123 <http://www.faqs.org/rfcs/rfc1123.html>`__,'
            ' section 2.1')
    )

    def __str__(self):
        return self.node_dns

    def remove_if_in_orion(self, logger=LOGGER):
        """
        if the domain controller host represented by this instance is also
        present on the `Orion` server, delete this istance

        We prefer to extract network node data from `Orion` instead of
        depending on some poor soul maintaining this model manually.

        There are some `AD` nodes in Orion that will match entries in this
        model but only if we consider the IP address. Since `AD` controllers
        always use fixed IP addresses (they better be), we will use IP
        addresses to eliminate the dupes.
        """
        ip_addresses = None

        try:
            ip_addresses = [
                addr[4][0] for addr in socket.getaddrinfo(self.node_dns, 0)
            ]
        except:  # pylint: disable=bare-except
            logger.error('Cannot resolve %s, deleting...', self)
            self.delete()
            return

        if OrionADNode.objects.filter(
                node__ip_address__in=ip_addresses).exists():

            logger.info(
                'Found %s within the Orion AD nodes, deleting...', self)
            self.delete()

        return

    class Meta:
        app_label = 'ldap_probe'
        verbose_name = _('Domain Controller not present in Orion')
        verbose_name_plural = _('Domain Controllers not present in Orion')
        ordering = ['node_dns', ]
        get_latest_by = 'updated_on'


class LdapProbeLog(models.Model):
    """
    :class:`django.db.models.Model` class used for storing LDAP probing
    information

    `LDAP Probe Log fields
    <../../../admin/doc/models/ldap_probe.ldapprobelog>`__
    """
    uuid = models.UUIDField(
        _('UUID'), unique=True, db_index=True, blank=False, null=False,
        default=get_uuid)
    ad_orion_node = models.ForeignKey(
        OrionADNode, db_index=True, blank=True, null=True,
        on_delete=models.CASCADE, verbose_name=_('AD controller (Orion)'))
    ad_node = models.ForeignKey(
        NonOrionADNode, db_index=True, blank=True, null=True,
        on_delete=models.CASCADE, verbose_name=_('AD controller'))
    elapsed_initialize = models.DecimalField(
        _('LDAP initialization duration'), max_digits=9, decimal_places=6,
        blank=True, null=True)
    elapsed_bind = models.DecimalField(
        _('LDAP bind duration'), max_digits=9, decimal_places=6,
        blank=True, null=True)
    elapsed_anon_bind = models.DecimalField(
        _('LDAP anonymous bind duration'), max_digits=9, decimal_places=6,
        blank=True, null=True)
    elapsed_read_root = models.DecimalField(
        _('LDAP read root DSE duration'), max_digits=9, decimal_places=6,
        blank=True, null=True)
    elapsed_search_ext = models.DecimalField(
        _('LDAP extended search duration'), max_digits=9, decimal_places=6,
        blank=True, null=True)
    ad_response = models.TextField(
        _('AD controller response'), blank=True, null=True)
    errors = models.TextField(
        _('Errors'), blank=True, null=True)
    created_on = models.DateTimeField(
        _('created on'), db_index=True, auto_now_add=True,
        help_text=_('object creation time stamp'))
    is_expired = models.BooleanField(
        _('Probe data has expired'), db_index=True, blank=False, null=False,
        default=False)
    failed = models.BooleanField(
        _('Probe failed'), db_index=True, blank=False, null=False,
        default=False)

    def __str__(self):
        return f'LDAP probe {self.uuid} to {self.node}'

    @property
    def node(self):
        """
        return the node that was the target of this `LDAP` probe
        """
        if self.ad_orion_node:
            return self.ad_orion_node.get_node()

        return self.ad_node.get_node()

    @property
    def perf_alert(self):
        """
        flag for considering if an instance of this class must trigger a
        performance alert

        :returns: `True/False`
        :rtype: bool
        """
        return any(
            [
                elapsed for elapsed in
                [
                    self_elapsed for self_elapsed in
                    [
                        self.elapsed_bind, self.elapsed_anon_bind,
                        self.elapsed_search_ext, self.elapsed_read_root
                    ]
                    if self_elapsed is not None
                ]
                if elapsed >= get_preference('ldapprobe__ldap_perf_alert')
            ]
        )

    @property
    def perf_warn(self):
        """
        flag for considering if an instance of this class must trigger a
        performance warning

        :returns: `True/False`
        :rtype: bool
        """
        return any(
            [
                elapsed for elapsed in
                [
                    self_elapsed for self_elapsed in
                    [
                        self.elapsed_bind, self.elapsed_anon_bind,
                        self.elapsed_search_ext, self.elapsed_read_root
                    ]
                    if self_elapsed is not None
                ]
                if elapsed >= get_preference('ldapprobe__ldap_perf_warn')
            ]
        )

    @property
    @mark_safe
    def absolute_url(self):
        """
        absolute `URL` for the `Django admin` form for this instance

        Note that there is no :class:`Django admin class
        <django.contrib.admin.ModelAdmin>` matching this model. We will
        have to use `admin views` pointing to the modles proxied from this
        model.

        :returns: the absolute `URL` for the admin pages showing this
            instance

        """
        admin_view = 'admin:ldap_probe_ldapprobeanonbindlog_change'

        if self.failed:
            admin_view = 'admin:ldap_probe_ldapprobelogfailed_change'

        if self.elapsed_bind:
            admin_view = 'admin:ldap_probe_ldapprobefullbindlog_change'

        return get_absolute_admin_change_url(
            admin_view=admin_view, obj_pk=self.id, obj_anchor_name=str(self))

    @property
    @mark_safe
    def ad_node_orion_url(self):
        """
        the `URL` for the `Orion` definition of the `AD` controller
        that was the destination of this probe
        """
        if self.ad_orion_node:
            return self.ad_orion_node.orion_url
        return None

    @classmethod
    def create_from_probe(cls, probe_data):
        """
        `class method
        <https://docs.python.org/3.6/library/functions.html#classmethod>`__
        that creates an instance of the :class:`LdapProbeLog`

        :arg probe_data: the data returned by the LDAP probe
        :type probe_data: :class:`ldap_probe.ad_probe.ADProbe`

        :arg logger: :class:`logging.Logger instance

        :returns: the new :class:`LdapProbeLog` instance
        """
        ldap_probe_log_entry = cls(
            elapsed_initialize=probe_data.elapsed.elapsed_initialize,
            elapsed_bind=probe_data.elapsed.elapsed_bind,
            elapsed_anon_bind=probe_data.elapsed.elapsed_anon_bind,
            elapsed_read_root=probe_data.elapsed.elapsed_read_root,
            elapsed_search_ext=probe_data.elapsed.elapsed_search_ext,
            ad_response=probe_data.ad_response, errors=probe_data.errors,
            failed=probe_data.failed
        )

        if isinstance(probe_data.ad_controller, OrionADNode):
            ldap_probe_log_entry.ad_orion_node = probe_data.ad_controller
        else:
            ldap_probe_log_entry.ad_node = probe_data.ad_controller

        try:
            ldap_probe_log_entry.save()
        except Exception as err:
            raise err

        return f'created {ldap_probe_log_entry}'

    class Meta:
        app_label = 'ldap_probe'
        verbose_name = _('AD service probe')
        verbose_name_plural = _('AD service probes')
        ordering = ('-created_on', )


class LdapProbeLogFailed(LdapProbeLog):
    """
    `Proxy model
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#proxy-models>`__
    that shows only :class:`LdapProbeLog` instances with full `AD` probe
    data
    """
    obejcts = LdapProbeLogFailedManager()

    class Meta:
        proxy = True
        verbose_name = _('Failed AD service probe')
        verbose_name_plural = _('Failed AD service probes')


class LdapProbeFullBindLog(LdapProbeLog):
    """
    `Proxy model
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#proxy-models>`__
    that shows only :class:`LdapProbeLog` instances with full `AD` probe
    data
    """
    obejcts = LdapProbeLogFullBindManager()

    class Meta:
        proxy = True
        verbose_name = _('AD service probe with full data')
        verbose_name_plural = _('AD service probes with full data')


class LdapProbeAnonBindLog(LdapProbeLog):
    """
    `Proxy model
    <https://docs.djangoproject.com/en/2.2/topics/db/models/#proxy-models>`__
    that shows only :class:`LdapProbeLog` instances with limited `AD` probe
    data
    """
    objects = LdapProbeLogAnonBindManager()

    class Meta:
        proxy = True
        verbose_name = _('AD service probe with limited data')
        verbose_name_plural = _('AD service probes with limited data')


class LdapCredError(BaseModel, models.Model):
    """
    :class:`django.db.models.Model` class used for storing LDAP errors
    related to invalid credentials

    See `Common Active Directory Bind Errors
    <https://ldapwiki.com/wiki/Common%20Active%20Directory%20Bind%20Errors>`__.

    `LDAP Probe Log fields
    <../../../admin/doc/models/ldap_probe.ldapcrederror>`__
    """
    error_unique_identifier = models.CharField(
        _('LDAP Error Subcode'), max_length=3, db_index=True, unique=True,
        blank=False, null=False)
    short_description = models.CharField(
        _('Short Description'), max_length=128, db_index=True, blank=False,
        null=False)
    comments = models.TextField(_('Comments'), blank=True, null=True)

    def __str__(self):
        return (
            f'data {self.error_unique_identifier}: {self.short_description}')

    class Meta:
        app_label = 'ldap_probe'
        verbose_name = _('Active Directory Bind Error')
        verbose_name_plural = _('Common Active Directory Bind Errors')
        ordering = ['error_unique_identifier', ]
