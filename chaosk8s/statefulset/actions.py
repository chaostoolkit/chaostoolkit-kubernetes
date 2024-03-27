import json
import logging
import os.path

import yaml
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException

from chaosk8s import create_k8s_api_client

__all__ = ["create_statefulset", "scale_statefulset", "remove_statefulset"]
logger = logging.getLogger("chaostoolkit")


def create_statefulset(
    spec_path: str, ns: str = "default", secrets: Secrets = None
):
    """
    Create a statefulset described by the service config, which must be
    the path to the JSON or YAML representation of the statefulset.
    """
    api = create_k8s_api_client(secrets)

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == ".json":
            statefulset = json.loads(f.read())
        elif ext in [".yml", ".yaml"]:
            statefulset = yaml.safe_load(f.read())
        else:
            raise ActivityFailed(f"cannot process {spec_path}")

    v1 = client.AppsV1Api(api)
    v1.create_namespaced_stateful_set(ns, body=statefulset)


def scale_statefulset(
    name: str, replicas: int, ns: str = "default", secrets: Secrets = None
):
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
            f"failed to scale '{name}' to {replicas} replicas: {str(e)}"
        )


def remove_statefulset(
    name: str = None,
    ns: str = "default",
    label_selector: str = None,
    secrets: Secrets = None,
):
    """
    Remove a statefulset by `name` or `label_selector` in the namespace `ns`.

    The statefulset is removed by deleting it without
        a graceful period to trigger an abrupt termination.

    If neither `name` nor `label_selector` is specified, all the statefulsets
    will be deleted in the namespace.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if name:
        ret = v1.list_namespaced_stateful_set(
            ns, field_selector=f"metadata.name={name}"
        )
    elif label_selector:
        ret = v1.list_namespaced_stateful_set(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_stateful_set(ns)

    logger.debug(
        f"Found {len(ret.items)} statefulset(s) named '{name}' in ns '{ns}'"
    )

    body = client.V1DeleteOptions()
    for d in ret.items:
        _ = v1.delete_namespaced_stateful_set(d.metadata.name, ns, body=body)
