import json

from chaoslib.types import Configuration, Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = ["get_nodes"]


def get_nodes(
    label_selector: str = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
):
    """
    List all Kubernetes worker nodes in your cluster. You may filter nodes
    by specifying a label selector.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_node(label_selector=label_selector, _preload_content=False)
    else:
        ret = v1.list_node(_preload_content=False)

    return json.loads(ret.read().decode("utf-8"))
