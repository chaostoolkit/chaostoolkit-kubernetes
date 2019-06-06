from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["delete_replica_set"]


def delete_replica_set(name: str, ns: str = "default",
                       label_selector: str = "name in ({name})",
                       secrets: Secrets = None):
    """
    Delete a replica set by `name` in the namespace `ns`.

    The replica set is deleted without a graceful period to trigger an abrupt termination.

    The selected resources are matched by the given `label_selector`.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)
    v1 = client.ExtensionsV1beta1Api(api)
    if label_selector:
        ret = v1.list_namespaced_replica_set(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_replica_set(ns)

    logger.debug("Found {d} replica sets named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for r in ret.items:
        v1.delete_namespaced_replica_set(r.metadata.name, ns, body)
