# -*- coding: utf-8 -*-
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["scale_statefulset", "remove_statefulset"]


def scale_statefulset(name: str, replicas: int, ns: str = "default",
                      secrets: Secrets = None):
    """
    Scale a stateful set up or down. The `name` is the name of the stateful
    set.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    body = {"spec": {"replicas": replicas}}
    try:
        v1.patch_namespaced_stateful_set(name, namespace=ns, body=body)
    except ApiException as e:
        raise ActivityFailed(
            "failed to scale '{s}' to {r} replicas: {e}".format(
                s=name, r=replicas, e=str(e)))


def remove_statefulset(name: str = None, ns: str = "default",
                       label_selector: str = None, secrets: Secrets = None):
    """
    Remove a statefulset by `name` in the namespace `ns`.

    The statefulset is removed by deleting it without
        a graceful period to trigger an abrupt termination.

    The selected resources are matched by the given `label_selector`.
    """
    field_selector = "metadata.name={name}".format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_stateful_set(
            ns, field_selector=field_selector,
            label_selector=label_selector)
    else:
        ret = v1.list_namespaced_stateful_set(ns,
                                              field_selector=field_selector)

    logger.debug("Found {d} statefulset(s) named '{n}' in ns '{s}'".format(
        d=len(ret.items), n=name, s=ns))

    body = client.V1DeleteOptions()
    for d in ret.items:
        res = v1.delete_namespaced_stateful_set(
            d.metadata.name, ns, body=body)
