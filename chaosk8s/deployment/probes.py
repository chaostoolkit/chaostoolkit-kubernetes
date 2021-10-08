from functools import partial
from typing import Union

import urllib3
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client, watch
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = [
    "deployment_available_and_healthy",
    "deployment_not_fully_available",
    "deployment_fully_available",
    "deployment_partially_available",
]


def deployment_available_and_healthy(
    name: str, ns: str = "default", label_selector: str = None, secrets: Secrets = None
) -> Union[bool, None]:
    """
    Lookup a deployment by `name` in the namespace `ns`.

    The selected resources are matched by the given `label_selector`.

    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the state is not
    as expected.
    """

    field_selector = f"metadata.name={name}"
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_deployment(
            ns, field_selector=field_selector, label_selector=label_selector
        )
    else:
        ret = v1.list_namespaced_deployment(ns, field_selector=field_selector)

    logger.debug(f"Found {len(ret.items)} deployment(s) named '{name}' in ns '{ns}'")

    if not ret.items:
        raise ActivityFailed(f"Deployment '{name}' was not found")

    for d in ret.items:
        logger.debug(
            f"Deployment has '{d.status.available_replicas}' available replicas"
        )

        if d.status.available_replicas != d.spec.replicas:
            raise ActivityFailed(f"Deployment '{name}' is not healthy")

    return True


def deployment_partially_available(
    name: str, ns: str = "default", label_selector: str = None, secrets: Secrets = None
) -> Union[bool, None]:
    """
    Check whether if the given deployment state is ready or at-least partially
    ready.
    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the state is not
    as expected.
    """

    field_selector = f"metadata.name={name}"
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_deployment(
            ns, field_selector=field_selector, label_selector=label_selector
        )
    else:
        ret = v1.list_namespaced_deployment(ns, field_selector=field_selector)

    logger.debug(f"Found {len(ret.items)} deployment(s) named '{name}' in ns '{ns}'")

    if not ret.items:
        raise ActivityFailed(f"Deployment '{name}' was not found")

    for d in ret.items:
        logger.debug(
            f"Deployment has '{d.status.available_replicas}' available replicas"
        )

        if d.status.available_replicas >= 1:
            return True
        else:
            raise ActivityFailed(f"Deployment '{name}' is not healthy")


def _deployment_readiness_has_state(
    name: str,
    ready: bool,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
) -> Union[bool, None]:
    """
    Check wether if the given deployment state is ready or not
    according to the ready paramter.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.ActivityFailed` exception is raised.
    """
    field_selector = f"metadata.name={name}"
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1Api(api)
    w = watch.Watch()
    timeout = int(timeout)

    if label_selector is None:
        watch_events = partial(
            w.stream,
            v1.list_namespaced_deployment,
            namespace=ns,
            field_selector=field_selector,
            _request_timeout=timeout,
        )
    else:
        label_selector = label_selector.format(name=name)
        watch_events = partial(
            w.stream,
            v1.list_namespaced_deployment,
            namespace=ns,
            field_selector=field_selector,
            label_selector=label_selector,
            _request_timeout=timeout,
        )

    try:
        logger.debug(f"Watching events for {timeout}s")
        for event in watch_events():
            deployment = event["object"]
            status = deployment.status
            spec = deployment.spec

            logger.debug(
                f"Deployment '{deployment.metadata.name}' {event['type']}: "
                f"Ready Replicas {status.ready_replicas} - "
                f"Unavailable Replicas {status.unavailable_replicas} - "
                f"Desired Replicas {spec.replicas}"
            )

            readiness = status.ready_replicas == spec.replicas
            if ready == readiness:
                w.stop()
                return True

    except urllib3.exceptions.ReadTimeoutError:
        logger.debug("Timed out!")
        return False


def deployment_not_fully_available(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
) -> Union[bool, None]:
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
            f"deployment '{name}' failed to stop running within {timeout}s"
        )


def deployment_fully_available(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
) -> Union[bool, None]:
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
        raise ActivityFailed(f"deployment '{name}' failed to recover within {timeout}s")
