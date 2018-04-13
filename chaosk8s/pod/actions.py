# -*- coding: utf-8 -*-
import json
import os.path
import random
import re
from typing import Union

from chaoslib.exceptions import FailedActivity
from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["terminate_pods"]


def terminate_pods(label_selector: str = None, name_pattern: str = None,
                   all: bool = False, rand: bool = False,
                   ns: str = "default", secrets: Secrets = None):
    """
    Terminate a pod gracefully. Select the appropriate pods by label and/or
    name patterns. Whenever a pattern is provided for the name, all pods
    retrieved will be filtered out if their name do not match the given
    pattern.

    If neither `label_selector` nor `name_pattern` are provided, all pods
    in the namespace will be terminated.

    If `all` is set to `True`, all matching pods will be terminated.
    If `rand` is set to `True`, one random pod will be terminated.
    Otherwise, the first retrieved pod will be terminated.
    """
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

    if rand:
        pods = [random.choice(pods)]
        logger.debug("Picked pod '{p}' to be terminated".format(
            p=pods[0].metadata.name))
    elif not all:
        pods = [pods[0]]
        logger.debug("Picked pod '{p}' to be terminated".format(
            p=pods[0].metadata.name))

    body = client.V1DeleteOptions()
    for p in pods:
        res = v1.delete_namespaced_pod(
            p.metadata.name, ns, body)
