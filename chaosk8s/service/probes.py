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


def service_is_initialized(name: str, ns: str = "default",
                           label_selector: str = "name in ({name})",
                           secrets: Secrets = None):
    """
    Lookup a service endpoint by its name and raises :exc:`FailedProbe` when
    the service was not found or not initialized.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_service(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_service(ns)

    logger.debug("Found {d} service(s) named '{n}' ins ns '{s}'".format(
        d=len(ret.items), n=name, s=ns))

    if not ret.items:
        raise ActivityFailed(
            "service '{name}' is not initialized".format(name=name))

    return True
