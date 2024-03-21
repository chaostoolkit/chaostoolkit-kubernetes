import json
import os.path

import yaml
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = [
    "create_daemon_set",
    "delete_daemon_set",
    "update_daemon_set",
]


def create_daemon_set(
    spec_path: str, ns: str = "default", secrets: Secrets = None
):
    """
    Create a daemon set described by the daemon set spec, which must be the
    path to the JSON or YAML representation of the daemon_set.
    """
    api = create_k8s_api_client(secrets)

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == ".json":
            daemon_set = json.loads(f.read())
        elif ext in [".yml", ".yaml"]:
            daemon_set = yaml.safe_load(f.read())
        else:
            raise ActivityFailed(f"cannot process {spec_path}")

    v1 = client.AppsV1Api(api)
    _ = v1.create_namespaced_daemon_set(ns, body=daemon_set)


def delete_daemon_set(
    name: str = None,
    ns: str = "default",
    label_selector: str = None,
    secrets: Secrets = None,
):
    """
    Delete a daemon set by `name` or `label_selector` in the namespace `ns`.

    The daemon set is deleted without a graceful period to trigger an abrupt
    termination.

    If neither `name` nor `label_selector` is specified, all the daemon sets
    will be deleted in the namespace.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)

    if name:
        ret = v1.list_namespaced_daemon_set(
            ns, field_selector=f"metadata.name={name}"
        )
    elif label_selector:
        ret = v1.list_namespaced_daemon_set(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_daemon_set(ns)

    logger.debug(f"Found {len(ret.items)} daemon sets named '{name}'")

    body = client.V1DeleteOptions()
    for d in ret.items:
        v1.delete_namespaced_daemon_set(d.metadata.name, ns, body=body)


def update_daemon_set(
    name: str, spec: dict, ns: str = "default", secrets: Secrets = None
):
    """
    Update the specification of the targeted daemon set according to spec.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    try:
        v1.patch_namespaced_daemon_set(name=name, namespace=ns, body=spec)
    except ApiException as e:
        raise ActivityFailed(f"failed to update daemon set '{name}': {str(e)}")
