"""
p_soc_auto.settings.development
-------------------------------

Development only Django settings for the :ref:`SOC Automation Server`

:copyright:

    Copyright 2018 - 2020 Provincial Health Service Authority
    of British Columbia

:contact:    daniel.busto@phsa.ca

"""
from p_soc_auto.settings.common import *

DEBUG = True
"""
Enable or disable debugging information
"""

ALLOWED_HOSTS = ['lvmsocdev01', 'lvmsocdev03', 'lvmsocq02', ]
"""
hosts that can be used to run development servers
"""