# -*- coding: utf-8 -*-
import datetime
import json
import math
import random
import re
from typing import Any, Dict, List

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL
from kubernetes.stream.ws_client import STDOUT_CHANNEL
from kubernetes.client.models.v1_pod import V1Pod
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["terminate_pods", "exec_in_pods"]


def terminate_pods(label_selector: str = None, name_pattern: str = None,
                   all: bool = False, rand: bool = False,
                   mode: str = "fixed", qty: int = 1,
                   grace_period: int = -1,
                   ns: str = "default", order: str = "alphabetic",
                   secrets: Secrets = None):
    """
    Terminate a pod gracefully. Select the appropriate pods by label and/or
    name patterns. Whenever a pattern is provided for the name, all pods
    retrieved will be filtered out if their name do not match the given
    pattern.

    If neither `label_selector` nor `name_pattern` are provided, all pods
    in the namespace will be selected for termination.

    If `all` is set to `True`, all matching pods will be terminated.

    Value of `qty` varies based on `mode`.
    If `mode` is set to `fixed`, then `qty` refers to number of pods to be
    terminated. If `mode` is set to `percentage`, then `qty` refers to
    percentage of pods, from 1 to 100, to be terminated.
    Default `mode` is `fixed` and default `qty` is `1`.

    If `order` is set to `oldest`, the retrieved pods will be ordered
    by the pods creation_timestamp, with the oldest pod first in list.

    If `rand` is set to `True`, n random pods will be terminated
    Otherwise, the first retrieved n pods will be terminated.

    If `grace_period` is greater than or equal to 0, it will
    be used as the grace period (in seconds) to terminate the pods.
    Otherwise, the default pod's grace period will be used.
    """

    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)

    pods = _select_pods(v1, label_selector, name_pattern,
                        all, rand, mode, qty, ns, order)

    body = client.V1DeleteOptions()
    if grace_period >= 0:
        body = client.V1DeleteOptions(grace_period_seconds=grace_period)

    for p in pods:
        v1.delete_namespaced_pod(p.metadata.name, ns, body=body)


def exec_in_pods(cmd: str,
                 label_selector: str = None, name_pattern: str = None,
                 all: bool = False, rand: bool = False,
                 mode: str = "fixed", qty: int = 1,
                 ns: str = "default", order: str = "alphabetic",
                 container_name: str = None,
                 request_timeout: int = 60,
                 secrets: Secrets = None) -> List[Dict[str, Any]]:
    """
    Execute the command `cmd` in the specified pod's container.
    Select the appropriate pods by label and/or name patterns.
    Whenever a pattern is provided for the name, all pods retrieved will be
    filtered out if their name do not match the given pattern.

    If neither `label_selector` nor `name_pattern` are provided, all pods
    in the namespace will be selected for termination.

    If `all` is set to `True`, all matching pods will be affected.

    Value of `qty` varies based on `mode`.
    If `mode` is set to `fixed`, then `qty` refers to number of pods affected.
    If `mode` is set to `percentage`, then `qty` refers to
    percentage of pods, from 1 to 100, to be affected.
    Default `mode` is `fixed` and default `qty` is `1`.

    If `order` is set to `oldest`, the retrieved pods will be ordered
    by the pods creation_timestamp, with the oldest pod first in list.

    If `rand` is set to `True`, n random pods will be affected
    Otherwise, the first retrieved n pods will be used
    """
    if not cmd:
        raise ActivityFailed("A command must be set to run a container")

    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)

    pods = _select_pods(v1, label_selector, name_pattern,
                        all, rand, mode, qty, ns, order)

    exec_command = cmd.strip().split()

    results = []
    for po in pods:
        logger.debug("Picked pods '{p}' for command execution {c}".format(
            p=po.metadata.name, c=exec_command))
        if not any(c.name == container_name for c in po.spec.containers):
            logger.debug("Pod {p} do not have container named '{n}'".format(
                p=po.metadata.name, n=container_name))
            continue

        pod_execution_result = {}
        # Use _preload_content to get back the raw JSON response.
        resp = stream.stream(v1.connect_get_namespaced_pod_exec,
                             po.metadata.name,
                             ns,
                             container=container_name,
                             command=exec_command,
                             stderr=True,
                             stdin=False,
                             stdout=True,
                             tty=False,
                             _preload_content=False)

        resp.run_forever(timeout=request_timeout)

        err = json.loads(resp.read_channel(ERROR_CHANNEL))
        out = resp.read_channel(STDOUT_CHANNEL)

        if err['status'] != "Success":
            error_code = err['details']['causes'][0]['message']
            error_message = err['message']
        else:
            error_code = 0
            error_message = ''

        results.append(dict(pod_name=po.metadata.name,
                            exit_code=error_code,
                            cmd=cmd,
                            stdout=out,
                            stderr=error_message))
    return results


###############################################################################
# Internals
###############################################################################
def _sort_by_pod_creation_timestamp(pod: V1Pod) -> datetime.datetime:
    """
    Function that serves as a key for the sort pods comparison
    """
    return pod.metadata.creation_timestamp


def _select_pods(v1: client.CoreV1Api = None, label_selector: str = None,
                 name_pattern: str = None,
                 all: bool = False, rand: bool = False,
                 mode: str = "fixed", qty: int = 1,
                 ns: str = "default",
                 order: str = "alphabetic") -> List[V1Pod]:

    # Fail if CoreV1Api is not instanciated
    if v1 is None:
        raise ActivityFailed("Cannot select pods. Client API is None")

    # Fail when quantity is less than 0
    if qty < 0:
        raise ActivityFailed(
            "Cannot select pods. Quantity '{q}' is negative.".format(q=qty))

    # Fail when mode is not `fixed` or `percentage`
    if mode not in ['fixed', 'percentage']:
        raise ActivityFailed(
            "Cannot select pods. Mode '{m}' is invalid.".format(m=mode))

    # Fail when order not `alphabetic` or `oldest`
    if order not in ['alphabetic', 'oldest']:
        raise ActivityFailed(
            "Cannot select pods. Order '{o}' is invalid.".format(o=order))

    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)
        logger.debug("Found {d} pods labelled '{s}' in ns {n}".format(
            d=len(ret.items), s=label_selector, n=ns))
    else:
        ret = v1.list_namespaced_pod(ns)
        logger.debug("Found {d} pods in ns '{n}'".format(
            d=len(ret.items), n=ns))

    pods = []
    if name_pattern:
        pattern = re.compile(name_pattern)
        for p in ret.items:
            if pattern.match(p.metadata.name):
                pods.append(p)
                logger.debug("Pod '{p}' match pattern".format(
                    p=p.metadata.name))
    else:
        pods = ret.items

    if order == 'oldest':
        pods.sort(key=_sort_by_pod_creation_timestamp)
    if not all:
        if mode == 'percentage':
            qty = math.ceil((qty * len(pods)) / 100)
        # If quantity is greater than number of pods present, cap the
        # quantity to maximum number of pods
        qty = min(qty, len(pods))

        if rand:
            pods = random.sample(pods, qty)
        else:
            pods = pods[:qty]

    return pods
