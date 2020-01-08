# -*- coding: utf-8 -*-
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException

from chaosk8s import create_k8s_api_client

__all__ = ["scale_statefulset"]


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
