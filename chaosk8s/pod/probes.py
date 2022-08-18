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
    "count_min_pods"
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
        f"Found {len(ret.items)} "
        f"pods: [{', '.join([p.metadata.name for p in ret.items])}] in ns '{ns}'"
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
        logger.debug(f"Fetching logs for pod '{name}'")
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
            f"Found {len(ret.items)} pods matching label '{label_selector}'"
            f" in ns '{ns}'"
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug(f"Found {len(ret.items)} pods in ns '{ns}'")

    if not ret.items:
        raise ActivityFailed(f"no pods '{label_selector}' were found")

    for d in ret.items:
        if d.status.phase != phase:
            raise ActivityFailed(
                f"pod '{label_selector}' is in phase '{d.status.phase}'"
                f" but should be '{phase}'"
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
            f"Found {len(ret.items)} pods matching label '{label_selector}'"
            f" in ns '{ns}'"
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug(f"Found {len(ret.items)} pods in ns '{ns}'")

    if not ret.items:
        raise ActivityFailed(f"no pods '{label_selector}' were found")

    for d in ret.items:
        # create a list of hash to compare with the given conditions
        pod_conditions = [
            {"type": pc.type, "status": pc.status} for pc in d.status.conditions
        ]
        for condition in conditions:
            if condition not in pod_conditions:
                raise ActivityFailed(
                    f"pod {d.metadata.name} does not match the following "
                    f"given condition: {condition}"
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
            f"Found {len(ret.items)} pods matching label '{label_selector}'"
            f" in ns '{ns}'"
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug(f"Found {len(ret.items)} pods in ns '{ns}'")

    if not ret.items:
        raise ActivityFailed(f"no pods '{label_selector}' were found")

    for d in ret.items:
        if d.status.phase == phase:
            raise ActivityFailed(
                f"pod '{label_selector}' should not be in phase '{d.status.phase}'"
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
            f"Found {len(ret.items)} pods matching label '{label_selector}'"
            f" in ns '{ns}'"
        )
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug(f"Found {len(ret.items)} pods in ns '{ns}'")

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

    logger.debug(f"Found {len(ret.items)} pod(s) named '{name}' in ns '{ns}")

    for p in ret.items:
        phase = p.status.phase
        logger.debug(f"Pod '{p.metadata.name}' has status '{phase}'")
        if phase == "Running":
            raise ActivityFailed(f"pod '{name}' is actually running")

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

    logger.debug(f"Found {len(failed)} failed and {len(not_ready)} not ready pods")

    # we probably should list them in the message
    if failed or not_ready:
        raise ActivityFailed("the system is unhealthy")

    return True


def count_min_pods(label_selector: str, phase: str = "Running", min_count: int=2,
               ns: str = "default", secrets: Secrets = None) -> bool:

    """
    Check if minimum number of pods are running.
    """

    count = count_pods( label_selector=label_selector, 
                        phase = phase,
                        ns = ns, 
                        secrets =secrets)
    return count >= min_count