# -*- coding: utf-8 -*-
from typing import Union

import urllib3
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from functools import partial
from kubernetes import client, watch
from logzero import logger

from chaosk8s import create_k8s_api_client
from chaosk8s.pod.probes import read_pod_logs

__all__ = ["deployment_available_and_healthy",
           "deployment_not_fully_available",
           "deployment_fully_available"]


def deployment_available_and_healthy(
        name: str, ns: str = "default",
        label_selector: str = None,
        secrets: Secrets = None) -> Union[bool, None]:
    """
    Lookup a deployment by `name` in the namespace `ns`.

    The selected resources are matched by the given `label_selector`.

    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the state is not
    as expected.
    """

    field_selector = "metadata.name={name}".format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_deployment(ns, field_selector=field_selector,
                                            label_selector=label_selector)
    else:
        ret = v1.list_namespaced_deployment(ns, field_selector=field_selector)

    logger.debug("Found {d} deployment(s) named '{n}' in ns '{s}'".format(
        d=len(ret.items), n=name, s=ns))

    if not ret.items:
        raise ActivityFailed(
            "Deployment '{name}' was not found".format(name=name))

    for d in ret.items:
        logger.debug("Deployment has '{s}' available replicas".format(
            s=d.status.available_replicas))

        if d.status.available_replicas != d.spec.replicas:
            raise ActivityFailed(
                "Deployment '{name}' is not healthy".format(name=name))

    return True


def _deployment_readiness_has_state(
        name: str, ready: bool,
        ns: str = "default",
        label_selector: str = None,
        timeout: int = 30,
        secrets: Secrets = None) -> Union[bool, None]:
    """
    Check wether if the given deployment state is ready or not
    according to the ready paramter.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.ActivityFailed` exception is raised.
    """
    field_selector = "metadata.name={name}".format(name=name)
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1Api(api)
    w = watch.Watch()
    timeout = int(timeout)

    if label_selector is None:
        watch_events = partial(w.stream, v1.list_namespaced_deployment,
                               namespace=ns,
                               field_selector=field_selector,
                               _request_timeout=timeout)
    else:
        label_selector = label_selector.format(name=name)
        watch_events = partial(w.stream, v1.list_namespaced_deployment,
                               namespace=ns,
                               field_selector=field_selector,
                               label_selector=label_selector,
                               _request_timeout=timeout)

    try:
        logger.debug("Watching events for {t}s".format(t=timeout))
        for event in watch_events():
            deployment = event['object']
            status = deployment.status
            spec = deployment.spec

            logger.debug(
                "Deployment '{p}' {t}: "
                "Ready Replicas {r} - "
                "Unavailable Replicas {u} - "
                "Desired Replicas {a}".format(
                    p=deployment.metadata.name, t=event["type"],
                    r=status.ready_replicas,
                    a=spec.replicas,
                    u=status.unavailable_replicas))

            readiness = status.ready_replicas == spec.replicas
            if ready == readiness:
                w.stop()
                return True

    except urllib3.exceptions.ReadTimeoutError:
        logger.debug("Timed out!")
        return False


def deployment_not_fully_available(
        name: str, ns: str = "default",
        label_selector: str = None,
        timeout: int = 30,
        secrets: Secrets = None) -> Union[bool, None]:
    """
    Wait until the deployment gets into an intermediate state where not all
    expected replicas are available. Once this state is reached, return `True`.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.ActivityFailed` exception is raised.
    """
    if _deployment_readiness_has_state(
        name,
        False,
        ns,
        label_selector,
        timeout,
        secrets,
    ):
        return True
    else:
        raise ActivityFailed(
            "deployment '{name}' failed to stop running within {t}s".format(
                name=name, t=timeout))


def deployment_fully_available(
        name: str, ns: str = "default",
        label_selector: str = None,
        timeout: int = 30,
        secrets: Secrets = None) -> Union[bool, None]:
    """
    Wait until all the deployment expected replicas are available.
    Once this state is reached, return `True`.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.ActivityFailed` exception is raised.
    """
    if _deployment_readiness_has_state(
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
            "deployment '{name}' failed to recover within {t}s".format(
                name=name, t=timeout))
