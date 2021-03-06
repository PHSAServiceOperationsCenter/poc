Mail Collector Application
==========================

The Mail Collector Application is responsible for collecting Windows
log events created by instances of the Mail Borg Client Application running on
remote monitoring bots, and for generating alerts and warnings with regards to
email and Exchange services availability at remote sites.

The application will also generate periodic reports with regards to  email
and Exchange services availability at remote sites.

The application is also capable of analyzing the availability of all and/or
various Exchange servers and Exchange databases based on the configurations
made available to the :ref:`Mail Borg Client Application` instances. 

This application is also responsible for providing main configurations for 
instances of the :ref:`Mail Borg Client Application` running on remote
monitoring bots.

The ``subscription`` services used by the :ref:`Mail Collector Application`
are provided via the :ref:`Subscription Services` component.

The ``email`` services used by the :ref:`Mail Collector Application`
are provided via the :ref:`Email Services` component.

  

.. toctree::
   :maxdepth: 2
   
   data_collection.rst
   alerts.rst
   reports.rst
   bot_config.rst   
   settings.rst
   dynamic_settings.rst
   celery.rst
   modules.rst
   
