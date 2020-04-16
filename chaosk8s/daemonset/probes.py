# -*- coding: utf-8 -*-
from typing import Union
import urllib3
from chaoslib.types import Secrets
from chaoslib.exceptions import ActivityFailed
from kubernetes import client
from logzero import logger
from chaosk8s import create_k8s_api_client

__all__ = ["daemonset_ready"]


def daemonset_ready(name: str, ns: str = "default",
                    label_selector: str = "name in ({name})",
                    timeout: int = 30,
                    secrets: Secrets = None):
    """
    Check that the DaemonSet has no misscheduled or unavailable pods

    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)

    ret = v1.list_namespaced_daemon_set(ns, label_selector=label_selector)
    logger.debug("Found {d} daemonsets".format(d=len(ret.items)))

    if not ret.items:
        raise ActivityFailed(
            "DaemonSet '{name}' was not found".format(name=name))

    for ds in ret.items:
        logger.debug("DaemonSet has '{u}' unavailable replicas and \
                     '{m}' misscheduled".format(
                     u=ds.status.number_unavailable,
                     m=ds.status.number_misscheduled))
        if (
           (ds.status.number_unavailable is not None
            and ds.status.number_unavailable != 0)
            or ds.status.number_misscheduled != 0
           ):
            raise ActivityFailed(
                                "DaemonSet has '{u}' unavailable replicas "
                                "and '{m}' misscheduled".format(
                                    u=ds.status.number_unavailable,
                                    m=ds.status.number_misscheduled))
    return True
