# -*- coding: utf-8 -*-
from typing import Union

import urllib3
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import MicroservicesStatus, Secrets
from kubernetes import client, watch
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["statefulset_fully_available"]


def _statefulset_readiness_has_state(name: str, ready: bool,
                                     ns: str = "default",
                                     label_selector: str = "name in ({name})",
                                     timeout: int = 30,
                                     secrets: Secrets = None):
    """
    Check wether if the given deployment state is ready or not
    according to the ready paramter.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.ActivityFailed` exception is raised.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1Api(api)
    w = watch.Watch()
    timeout = int(timeout)

    try:
        logger.debug("Watching events for {t}s".format(t=timeout))
        for event in w.stream(v1.list_namespaced_stateful_set, namespace=ns,
                              label_selector=label_selector,
                              _request_timeout=timeout):
            statefulset = event['object']
            status = statefulset.status
            spec = statefulset.spec

            logger.debug(
                "StatefulSet '{p}' {t}: "
                "Ready Replicas {r} - "
                "Desired Replicas {a}".format(
                    p=statefulset.metadata.name, t=event["type"],
                    r=status.ready_replicas,
                    a=spec.replicas))

            readiness = status.ready_replicas == spec.replicas
            if ready == readiness:
                w.stop()
                return True

    except urllib3.exceptions.ReadTimeoutError:
        logger.debug("Timed out!")
        return False


def statefulset_is_fully_available(name: str, ns: str = "default",
                                   label_selector: str = "name in ({name})",
                                   timeout: int = 30,
                                   secrets: Secrets = None):
    """
    Wait until the StatefulSet gets into an intermediate state where all
    expected replicas are available. Once this state is reached, return `True`.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.ActivityFailed` exception is raised.
    """
    if _statefulset_readiness_has_state(
        name,
        True,
        ns,
        label_selector,
        timeout,
        secrets,
    ):
        return True
    else:
        raise ActivityFailed(
            "StatefulSet '{name}' failed to recover within {t}s".format(
                name=name, t=timeout))
