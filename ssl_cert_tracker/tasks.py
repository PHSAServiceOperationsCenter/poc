"""
.. _models:

django models for the ssl_certificates app

:module:    new_tasks.py

:copyright:

    Copyright 2018 Provincial Health Service Authority
    of British Columbia

:contact:    ali.rahmat@phsa.ca

"""

import logging

import xml.dom.minidom
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import MaxRetriesExceededError
from libnmap.process import NmapProcess
from orion_integration.lib import OrionSslNode

from .db_helper import insert_into_certs_data

from .utils import process_xml_cert

logger = get_task_logger(__name__)

SSL_PROBE_OPTIONS = r'-Pn -p 443 --script ssl-cert'


class NmapError(Exception):
    """
    raise on nmap failure
    """
    pass


class NmapXMLError(Exception):
    """
    raise when the XML report from nmap cannot be processed
    """
    pass


class NoSSLCertOnNodeError(Exception):
    """
    raise if there is no SSL certificate on the node probed by nmap
    """
    pass


class SSLDatabaseError(Exception):
    """
    raise if one cannot update the database with the SSL certificate
    collected with nmap
    """
    pass


class OrionDataError(Exception):
    """
    raise when there are no orion nodes available for nmap probing
    """
    pass


@shared_task(
    rate_limit='0.5/s', queue='nmap', autoretry_for=(NmapError,),
    max_retries=3, retry_backoff=True)
def go_node(node_id, node_address):
    """
    collect SSL certificate data as returned by nmap and save it to the
    database
    """
    try:
        nmap_task = NmapProcess(node_address, options=SSL_PROBE_OPTIONS)
        nmap_task.run()
    except MaxRetriesExceededError as error:
        logger.error(
            'nmap retry limit exceeded for node address %s' % node_address)
        raise error
    except Exception as ex:
        raise NmapError(
            'nmap error for node address %s: %s' % (node_address, str(ex)))

    try:
        json = process_xml_cert(
            node_id, xml.dom.minidom.parseString(nmap_task.stdout))
    except Exception as error:
        logging.error(
            'cannot process nmap XML report for node address %s: %s'
            % (node_address, str(error)))

    if json["md5"] is None:
        raise NoSSLCertOnNodeError(
            'could not retrieve SSL certificate from node address %s'
            % node_address)

    import ipdb
    ipdb.set_trace()
    try:
        insert_into_certs_data(json)
    except Exception as error:
        raise SSLDatabaseError(
            'cannot insert/update SSL information collected from node'
            ' address %s' % node_address)

    return 'successful SSL nmap probe on node address %s' % node_address


@shared_task(queue='ssl')
def getnmapdata():
    """
    get the orion node information that will be used for nmap probes

    #TODO: rename this to get_orion_nodes()
    #TODO: replace the go_node.delay() loop with a celery group
    """
    nodes = OrionSslNode.nodes()
    if not nodes:
        raise OrionDataError(
            'there are no Orion nodes available for SSL nmap probing')

    for node in nodes:
        go_node.delay(node.id, node.ip_address)

    return 'queued SSL nmap probes for %s Orion nodes' % len(nodes)
