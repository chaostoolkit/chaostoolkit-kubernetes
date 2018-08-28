# -*- coding: utf-8 -*-
import math
import random
import re

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["terminate_pods"]


def terminate_pods(label_selector: str = None, name_pattern: str = None,
                   all: bool = False, rand: bool = False,
                   mode: str = "fixed", qty: int = 1,
                   ns: str = "default", secrets: Secrets = None):
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

    If `rand` is set to `True`, n random pods will be terminated
    Otherwise, the first retrieved n pods will be terminated.
    """
    # Fail when quantity is less than 0
    if qty < 0:
        raise ActivityFailed(
            "Cannot terminate pods. Quantity '{q}' is negative.".format(q=qty))
    # Fail when mode is not `fixed` or `percentage`
    if mode not in ['fixed', 'percentage']:
        raise ActivityFailed(
            "Cannot terminate pods. Mode '{m}' is invalid.".format(m=mode))
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(ns, label_selector=label_selector)

    logger.debug("Found {d} pods labelled '{s}'".format(
        d=len(ret.items), s=label_selector))

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

    logger.debug("Picked pods '{p}' to be terminated".format(
        p=",".join([po.metadata.name for po in pods])))

    body = client.V1DeleteOptions()
    for p in pods:
        res = v1.delete_namespaced_pod(
            p.metadata.name, ns, body)
