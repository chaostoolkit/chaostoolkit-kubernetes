from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["delete_replica_set"]


def delete_replica_set(
    name: str = None,
    ns: str = "default",
    label_selector: str = None,
    secrets: Secrets = None,
):
    """
    Delete a replica set by `name` or `label_selector` in the namespace `ns`.

    The replica set is deleted without a graceful period to trigger an abrupt
    termination.

    If neither `name` nor `label_selector` is specified, all the replica sets
    will be deleted in the namespace.
    """
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1Api(api)
    if name:
        ret = v1.list_namespaced_replica_set(ns, field_selector=f"metadata.name={name}")
    elif label_selector:
        ret = v1.list_namespaced_replica_set(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_replica_set(ns)

    logger.debug(f"Found {len(ret.items)} replica sets named '{name}'")

    body = client.V1DeleteOptions()
    for r in ret.items:
        v1.delete_namespaced_replica_set(r.metadata.name, ns, body=body)
