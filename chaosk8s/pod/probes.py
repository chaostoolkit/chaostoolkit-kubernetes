# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict, List, Union

import dateparser
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import MicroservicesStatus, Secrets
from kubernetes import client
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = [
    "pods_in_phase",
    "pods_in_conditions",
    "pods_not_in_phase",
    "read_pod_logs",
    "count_pods",
    "pod_is_not_available",
]


def read_pod_logs(
    name: str = None,
    last: Union[str, None] = None,
    ns: str = "default",
    from_previous: bool = False,
    label_selector: str = "name in ({name})",
    container_name: str = None,
    secrets: Secrets = None,
) -> Dict[str, str]:
    """
    Fetch logs for all the pods with the label `"name"` set to `name` and
    return a dictionary with the keys being the pod's name and the values
    the logs of said pod. If `name` is not provided, use only the
    `label_selector` instead.

    When your pod has several containers, you should also set `container_name`
    to clarify which container you want to read logs from.

    If you provide `last`, this returns the logs of the last N seconds
    until now. This can set to a fluent delta such as `10 minutes`.

    You may also set `from_previous` to `True` to capture the logs of a
    previous pod's incarnation, if any.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)

    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)

    else:
        ret = v1.list_namespaced_pod(ns)

    logger.debug(
        "Found {d} pods: [{p}] in ns '{n}'".format(
            d=len(ret.items), n=ns, p=", ".join([p.metadata.name for p in ret.items])
        )
    )

    since = None
    if last:
        now = datetime.now()
        since = int((now - dateparser.parse(last)).total_seconds())

    params = dict(
        namespace=ns,
        follow=False,
        previous=from_previous,
        timestamps=True,
        container=container_name or "",  # None is not a valid value
        _preload_content=False,
    )

    if since:
        params["since_seconds"] = since

    logs = {}
    for p in ret.items:
        name = p.metadata.name
        logger.debug("Fetching logs for pod '{n}'".format(n=name))
        r = v1.read_namespaced_pod_log(name, **params)
        logs[name] = r.read().decode("utf-8")

    return logs


def pods_in_phase(
    label_selector: str,
    phase: str = "Running",
    ns: str = "default",
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a pod by `label_selector` in the namespace `ns`.

    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)
        logger.debug(
            "Found {d} pods matching label '{n}' in ns '{s}'".format(
                d=len(ret.items), n=label_selector, s=ns
            )
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug("Found {d} pods in ns '{n}'".format(d=len(ret.items), n=ns))

    if not ret.items:
        raise ActivityFailed("no pods '{name}' were found".format(name=label_selector))

    for d in ret.items:
        if d.status.phase != phase:
            raise ActivityFailed(
                "pod '{name}' is in phase '{s}' but should be '{p}'".format(
                    name=label_selector, s=d.status.phase, p=phase
                )
            )

    return True


def pods_in_conditions(
    label_selector: str,
    conditions: List[Dict[str, str]],
    ns: str = "default",
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a pod by `label_selector` in the namespace `ns`.

    Raises :exc:`chaoslib.exceptions.ActivityFailed` if one of the given
    conditions type/status is not as expected
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)
        logger.debug(
            "Found {d} pods matching label '{n}' in ns '{s}'".format(
                d=len(ret.items), n=label_selector, s=ns
            )
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug("Found {d} pods in ns '{n}'".format(d=len(ret.items), n=ns))

    if not ret.items:
        raise ActivityFailed("no pods '{name}' were found".format(name=label_selector))

    for d in ret.items:
        # create a list of hash to compare with the given conditions
        pod_conditions = [
            {"type": pc.type, "status": pc.status} for pc in d.status.conditions
        ]
        for condition in conditions:
            if condition not in pod_conditions:
                raise ActivityFailed(
                    "pod {name} does not match the following "
                    "given condition: {condition}".format(
                        name=d.metadata.name, condition=condition
                    )
                )

    return True


def pods_not_in_phase(
    label_selector: str,
    phase: str = "Running",
    ns: str = "default",
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a pod by `label_selector` in the namespace `ns`.

    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the pod is in the
    given phase and should not have.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)
        logger.debug(
            "Found {d} pods matching label '{n}' in ns '{s}'".format(
                d=len(ret.items), n=label_selector, s=ns
            )
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug("Found {d} pods in ns '{n}'".format(d=len(ret.items), n=ns))

    if not ret.items:
        raise ActivityFailed("no pods '{name}' were found".format(name=label_selector))

    for d in ret.items:
        if d.status.phase == phase:
            raise ActivityFailed(
                "pod '{name}' should not be in phase '{s}'".format(
                    name=label_selector, s=d.status.phase
                )
            )

    return True


def count_pods(
    label_selector: str, phase: str = None, ns: str = "default", secrets: Secrets = None
) -> int:
    """
    Count the number of pods matching the given selector in a given `phase`, if
    one is given.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)
        logger.debug(
            "Found {d} pods matching label '{n}' in ns '{s}'".format(
                d=len(ret.items), n=label_selector, s=ns
            )
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug("Found {d} pods in ns '{n}'".format(d=len(ret.items), n=ns))

    if not ret.items:
        return 0

    if not phase:
        return len(ret.items)

    count = 0
    for d in ret.items:
        if d.status.phase == phase:
            count = count + 1

    return count


def pod_is_not_available(
    name: str,
    ns: str = "default",
    label_selector: str = "name in ({name})",
    secrets: Secrets = None,
) -> bool:
    """
    Lookup pods with a `name` label set to the given `name` in the specified
    `ns`.

    Raises :exc:`chaoslib.exceptions.ActivityFailed` when one of the pods
    with the specified `name` is in the `"Running"` phase.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_pod(ns)

    logger.debug(
        "Found {d} pod(s) named '{n}' in ns '{s}".format(d=len(ret.items), n=name, s=ns)
    )

    for p in ret.items:
        phase = p.status.phase
        logger.debug("Pod '{p}' has status '{s}'".format(p=p.metadata.name, s=phase))
        if phase == "Running":
            raise ActivityFailed("pod '{name}' is actually running".format(name=name))

    return True


def all_pods_healthy(
    ns: str = "default", secrets: Secrets = None
) -> MicroservicesStatus:
    """
    Check all pods in the system are running and available.

    Raises :exc:`chaoslib.exceptions.ActivityFailed` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)
    not_ready = []
    failed = []

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(namespace=ns)
    for p in ret.items:
        phase = p.status.phase
        if phase == "Failed":
            failed.append(p)
        elif phase not in ("Running", "Succeeded"):
            not_ready.append(p)

    logger.debug(
        "Found {d} failed and {n} not ready pods".format(
            d=len(failed), n=len(not_ready)
        )
    )

    # we probably should list them in the message
    if failed or not_ready:
        raise ActivityFailed("the system is unhealthy")

    return True
