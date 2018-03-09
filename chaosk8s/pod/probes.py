# -*- coding: utf-8 -*-
from datetime import datetime
import json
from typing import Dict, Union
import urllib3

from chaoslib.types import Secrets
import dateparser
from logzero import logger
from kubernetes import client, watch

from chaosk8s import create_k8s_api_client
from chaoslib.exceptions import FailedActivity


__all__ = ["pods_in_phase", "pods_not_in_phase", "read_pod_logs"]


def read_pod_logs(name: str=None, last: Union[str, None]=None,
                  ns: str="default", from_previous: bool=False,
                  label_selector: str="name in ({name})",
                  container_name: str=None,
                  secrets: Secrets=None) -> Dict[str, str]:
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
    ret = v1.list_namespaced_pod(ns, label_selector=label_selector)

    logger.debug("Found {d} pods: [{p}]".format(
        d=len(ret.items), p=', '.join([p.metadata.name for p in ret.items])))

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
        _preload_content=False
    )

    if since:
        params["since_seconds"] = since

    logs = {}
    for p in ret.items:
        name = p.metadata.name
        logger.debug("Fetching logs for pod '{n}'".format(n=name))
        r = v1.read_namespaced_pod_log(name, **params)
        logs[name] = r.read().decode('utf-8')

    return logs


def pods_in_phase(label_selector: str, phase: str = "Running",
                  ns: str = "default", secrets: Secrets = None) -> bool:
    """
    Lookup a pod by `label_selector` in the namespace `ns`.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(ns, label_selector=label_selector)

    logger.debug("Found {d} pods matching label '{n}'".format(
        d=len(ret.items), n=label_selector))

    if not ret.items:
        raise FailedActivity(
            "no pods '{name}' were found".format(name=label_selector))

    for d in ret.items:
        if d.status.phase != phase:
            raise FailedActivity(
                "pod '{name}' is in phase '{s}' but should be '{p}'".format(
                    name=label_selector, s=d.status.phase, p=phase))

    return True


def pods_not_in_phase(label_selector: str, phase: str = "Running",
                      ns: str = "default", secrets: Secrets = None) -> bool:
    """
    Lookup a pod by `label_selector` in the namespace `ns`.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when the pod is in the
    given phase and should not have.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(ns, label_selector=label_selector)

    logger.debug("Found {d} pods matching label '{n}'".format(
        d=len(ret.items), n=label_selector))

    if not ret.items:
        raise FailedActivity(
            "no pods '{name}' were found".format(name=label_selector))

    for d in ret.items:
        if d.status.phase == phase:
            raise FailedActivity(
                "pod '{name}' should not be in phase '{s}'".format(
                    name=label_selector, s=d.status.phase))

    return True
