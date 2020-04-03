"""
.. _config:

:module:    mail_borg.config

:copyright:

    Copyright 2018 - 2019 Provincial Health Service Authority
    of British Columbia

:contact:    daniel.busto@phsa.ca

Configuration module for the :ref:`Mail Borg Client Application`

.. todo::

    there are some constants that need to move into the local configuration
"""
import collections
import configparser
import json
import socket

from requests import Session, urllib3, ConnectTimeout, ConnectionError

HTTP_PROTO = 'http'
"""
:class:`str` HTTP_PROTO determines if we use http or https to connect to the
configuration server

"""
VERIFY_SSL = False
"""
:class:`bool` VERIFY_SSL: check the validity of the SSL certificate when
using https
"""

SESSION = Session()
"""
:class:`requests.Session` SESSION: cached Session object to be reused by all
http connections
"""

SESSION.headers = {'Content-Type': 'application/json'}
if not SESSION.verify:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOCAL_CONFIG = 'mail_borg.json'
"""
:class:`str` LOCAL_CONFIG is the name of the file used to cache the
configuration downloaded from the ``SOC Automation server``. This is the
configuration that will be used if loading the configuration from the server
is disabled
"""

WIN_EVT_CFG = dict(
    app_name='BorgExchangeMonitor',
    log_type='Application',
    evt_log_key='\\SYSTEM\\CurentControlSet\\Service\\EventLog',
    msg_dll=None)
"""
:class:`dict` WIN_EVENT_CFG contains the settings required for writing to the
Windows event log

:key app_name: the value of the application property in the event log

:key log_type: which windows log will be used for writing the events

:key evt_log_key: Windows registry key for the events log

:key msg_dll:

    Windows resources for providing descriptions when writing log events.
    If ``None``, the default DLL will be used

"""

INI_DEFAULTS = dict(use_cfg_srv=True,
                    cfg_srv_ip='10.2.50.38',
                    cfg_srv_port=8080,
                    cfg_srv_conn_timeout=30,
                    cfg_srv_read_timeout=120)
"""
:class:`dict` INI_DEFAULTS are the local configuration values that will be
used to overwrite the ``mail_borg.ini`` configuration file when the user
clicks on the ``Reset local config`` button
"""


class ConfigManager:
    """
    A middleman to handle the access to various different configuration sources
    for the mail borg application
    """
    def __init__(self):
        """
        Constructor for ConfigManager
        """
        self.server_config = self._load_server_configuration()
        self.server = ConfigServer(self.server_config)
        # TODO what to do about local config?
        self.local = False

    @property
    def app_config(self):
        """
        The configuration for the mail borg application
        """
        if self.local:
            return None
        return self.server.config

    @staticmethod
    def _load_server_configuration(config_file='mail_borg.ini', section='SITE'):
        """
        Load (or reload) the basic configuration required for bootstrapping
        the :ref:`Mail Borg Client Application`

        There are three potential sources for the basic configuration:

        * a configuration file using the INI format

        * the :attr:`INI_DEFAULTS` defined in this module

        * the basic configuration fields from the :mod:`mail_borg.mail_borg_gui`
          module

        :arg dict current_base_configuration:

            If present, it represents the contents of the basic config fields
            from the main window of the :mod:`mail_borg.mail_borg_gui` module.
            if this argument is present, the function will return it.

            This argument is used under scenarios where the user has changed the
            initial basic configuration (e.g. the address of the configuration
            server), and now desires the preserve the new configuration

        :arg str config_file:

            The name of the INI file containing the basic configuration

            Default is 'mail_borg.ini'. If the INI file cannot be loaded,
            the values from :attr:`INI_DEFAULTS` will be returned

        :arg str section:

            The INI file section containing the basic configuration

            Default value is 'SITE'

        :returns: :class:`dict` with the basic configuration
        """
        config = dict()

        config_parser = configparser.ConfigParser(allow_no_value=True,
                                                  empty_lines_in_values=False)
        loaded = config_parser.read(config_file)

        if not loaded:
            return dict(INI_DEFAULTS)

        config['use_cfg_srv'] = config_parser.getboolean(section, 'use_cfg_srv')
        config['cfg_srv_ip'] = config_parser.get(section, 'cfg_srv_ip')
        config['cfg_srv_port'] = config_parser.getint(section, 'cfg_srv_port')
        config['cfg_srv_conn_timeout'] = config_parser.getint(
            section, 'cfg_srv_conn_timeout')
        config['cfg_srv_read_timeout'] = config_parser.getint(
            section, 'cfg_srv_read_timeout')

        return config

    def clear_config(self):
        """
        Remove all application configuration values
        """
        self.server.clear_config()

    def reset_server_configuration(self):
        """
        reload the basic configuration from the :attr:`INI_DEFAULTS

        :returns: :class:`dict` with the default basic configuration
        """
        self.server_config = dict(INI_DEFAULTS)

        self.save_server_configuration()

    def save_server_configuration(self, config_file='mail_borg.ini'):
        """
        save the server configuration to an INI file

        :arg str config_file:

            The name of the INI file containing the basic configuration.
            Default is 'mail_borg.ini'.
        """
        config_parser = configparser.ConfigParser(
            allow_no_value=True, empty_lines_in_values=False)
        config_parser.read_dict(
            collections.OrderedDict(('SITE', self.server_config)),
            source='<collections.OrderedDict>')

        with open(config_file, 'w') as file:
            config_parser.write(file, space_around_delimiters=True)


class ConfigServer:
    """
    Class that manages interactions with the server that stores the application
    configuration.
    """
    def __init__(self, srv_config):
        """
        Constructor for config server

        :param srv_config: Configuration for the server connection
        """
        self.ip = srv_config['cfg_srv_ip'] # pylint: disable=invalid-name
        self.port = srv_config['cfg_srv_port']
        self.connection_timeout = srv_config['cfg_srv_conn_timeout']
        self.read_timeout = srv_config['cfg_srv_read_timeout']
        self._config = None
        self.status = 'No config loaded'

    @property
    def config(self):
        """
        App configuration as stored on the server.
        """
        if not self._config:
            self._load_config()
        return self._config

    def _load_config(self):
        """
        load the main configuration for the :ref:`Mail Borg Client Application`

        See :ref:`borg_remote_config` for more details about the structure of
        the main configuration.
        """
        self._config = dict()

        url = self._rest_url()

        try:
            response = SESSION.get(
                url, timeout=(self.connection_timeout, self.read_timeout))
        except (ConnectTimeout, ConnectionError) as server_err:
            self.status = f'Could not load config from server, ' \
                                    f'{server_err}. '
        else:
            if not response.json():  # if there is no json data in the response
                # there is no config on server
                # TODO check status instead?
                self.status = f'Could not find configuration for ' \
                              f'{socket.gethostname()} on server.'
                return

            self._config = response.json()[0]

            self.status = ('Loaded configuration %s from server' %
                           self.config['exchange_client_config']['config_name'])

            with open(LOCAL_CONFIG, 'w') as local_config:
                json.dump(self._config, local_config, indent=4)

    def _rest_url(self):
        """
        The URL to use to retrieve the configuration
        """
        rest_endpoint = 'mail_collector/api/get_config'
        SESSION.verify = VERIFY_SSL
        hostname = socket.gethostname()

        return f'{HTTP_PROTO}://{self.ip}:{self.port}/{rest_endpoint}/' \
               f'{hostname}/'

    def clear_config(self):
        """
        Remove the config from the object.
        Does not affect the configuration file on server.
        """
        self._config = None
