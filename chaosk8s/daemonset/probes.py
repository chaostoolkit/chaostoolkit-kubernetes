from functools import partial

import urllib3
from chaoslib.types import Secrets
from kubernetes import client, watch
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = [
    "daemon_set_available_and_healthy",
    "daemon_set_not_fully_available",
    "daemon_set_fully_available",
    "daemon_set_partially_available",
]


def daemon_set_available_and_healthy(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a daemon set by `name` in the namespace `ns`.

    The selected resources are matched by the given `label_selector`.

    Return `True` if daemon set is available, otherwise `False`.

    """

    field_selector = f"metadata.name={name}"
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_daemon_set(
            ns, field_selector=field_selector, label_selector=label_selector
        )
    else:
        ret = v1.list_namespaced_daemon_set(ns, field_selector=field_selector)

    logger.debug(
        f"Found {len(ret.items)} daemon_set(s) named '{name}' in ns '{ns}'"
    )

    if not ret.items:
        logger.debug(f"daemon set '{name}' was not found")
        return False

    for d in ret.items:
        logger.debug(f"daemon set has '{d.status.number_ready}' available pods")

        if d.status.number_ready != d.status.desired_number_scheduled:
            logger.debug(f"daemon set '{name}' is not healthy")
            return False

    return True


def daemon_set_partially_available(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    secrets: Secrets = None,
) -> bool:
    """
    Check whether if the given daemon set state is ready or at-least partially
    ready. Return `True` if dameon set is partially available, otherwise `False`
    """

    field_selector = f"metadata.name={name}"
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_daemon_set(
            ns, field_selector=field_selector, label_selector=label_selector
        )
    else:
        ret = v1.list_namespaced_daemon_set(ns, field_selector=field_selector)

    logger.debug(
        f"Found {len(ret.items)} daemon_set(s) named '{name}' in ns '{ns}'"
    )

    if not ret.items:
        logger.debug(f"daemon set '{name}' was not found")
        return False

    for d in ret.items:
        logger.debug(f"daemon set has '{d.status.number_ready}' ready pods")

        if d.status.number_ready >= 1:
            return True
        else:
            logger.debug(f"daemon set '{name}' is not healthy")
            return False

    return False


def _daemon_set_readiness_has_state(
    name: str,
    ready: bool,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
) -> bool:
    """
    Check wether if the given daemon_set state is ready or not
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
            v1.list_namespaced_daemon_set,
            namespace=ns,
            field_selector=field_selector,
            _request_timeout=timeout,
        )
    else:
        label_selector = label_selector.format(name=name)
        watch_events = partial(
            w.stream,
            v1.list_namespaced_daemon_set,
            namespace=ns,
            field_selector=field_selector,
            label_selector=label_selector,
            _request_timeout=timeout,
        )

    try:
        logger.debug(f"Watching events for {timeout}s")
        for event in watch_events():
            daemon_set = event["object"]
            status = daemon_set.status

            logger.debug(
                f"daemon set '{daemon_set.metadata.name}' {event['type']}: "
                f"Available pods {status.number_ready} - "
                f"Unavailable pods {status.number_unavailable} - "
                f"Desired scheduled pods {status.desired_number_scheduled}"
            )

            readiness = status.number_ready == status.desired_number_scheduled
            if ready == readiness:
                w.stop()
                return True

    except urllib3.exceptions.ReadTimeoutError:
        logger.debug("Timed out!")
        return False

    return False


def daemon_set_not_fully_available(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
) -> bool:
    """
    Wait until the daemon set gets into an intermediate state where not all
    expected replicas are available. Once this state is reached, return `True`.
    If the state is not reached after `timeout` seconds, return `False`.
    """
    if _daemon_set_readiness_has_state(
        name,
        False,
        ns,
        label_selector,
        timeout,
        secrets,
    ):
        return True
    else:
        logger.debug(
            f"daemon set '{name}' failed to stop running within {timeout}s"
        )
        return False


def daemon_set_fully_available(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
) -> bool:
    """
    Wait until all the daemon set expected replicas are available.
    Once this state is reached, return `True`.
    If the state is not reached after `timeout` seconds, return `False`
    """
    if _daemon_set_readiness_has_state(
        name,
        True,
        ns,
        label_selector,
        timeout,
        secrets,
    ):
        return True
    else:
        logger.debug(f"daemon set '{name}' failed to recover within {timeout}s")
        return False
