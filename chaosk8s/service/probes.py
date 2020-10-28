# -*- coding: utf-8 -*-
from typing import Union

import urllib3
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client, watch
from logzero import logger

from chaosk8s import create_k8s_api_client
from chaosk8s.pod.probes import read_pod_logs, pod_is_not_available

__all__ = ["service_is_initialized"]


def service_is_initialized(name: str = None, ns: str = "default",
                           label_selector: str = None,
                           secrets: Secrets = None):
    """
    Lookup a service endpoint by its name and raises :exc:`FailedProbe` when
    the service was not found or not initialized.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    if name and not label_selector:
        logger.debug("Filtering services by name %s".format(name))
        ret = v1.list_namespaced_service(ns,
            field_selector="metadata.name={}".format(name))
        logger.debug("Found {d} service(s) named '{n}' in ns '{s}'".format(
            d=len(ret.items), n=name, s=ns))
    elif label_selector and not name:
        logger.debug("Filtering services by label %s".format(label_selector))
        ret = v1.list_namespaced_service(ns, label_selector=label_selector)
        logger.debug("Found {d} service(s) in ns '{s}' labelled '{l}'".format(
            d=len(ret.items), s=ns, l=label_selector))
    elif name and label_selector:
        logger.debug(
            "Filtering services by name %s and label %s".format(
                name, label_selector))
        ret = v1.list_namespaced_service(ns,
            field_selector="metadata.name={}".format(name),
            label_selector=label_selector)
        logger.debug(
            "Found {d} service(s) named '{n}' and labelled '{l}' "
            "in ns '{s}'".format(d=len(ret.items), n=name, l=label_selector,
            s=ns))
    else:
        ret = v1.list_namespaced_service(ns)
        logger.debug("Found {d} service(s) in ns '{s}'".format(
            d=len(ret.items), s=ns))

    if not ret.items:
        raise ActivityFailed(
            "service '{name}' is not initialized".format(name=name))

    return True
