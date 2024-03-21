import json
import logging
from typing import Dict, List

from chaoslib.types import Configuration, Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = [
    "get_nodes",
    "all_nodes_must_be_ready_to_schedule",
    "get_all_node_status_conditions",
]
logger = logging.getLogger("chaostoolkit")


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
        ret = v1.list_node(
            label_selector=label_selector, _preload_content=False
        )
    else:
        ret = v1.list_node(_preload_content=False)

    return json.loads(ret.read().decode("utf-8"))


def get_all_node_status_conditions(
    configuration: Configuration = None, secrets: Secrets = None
) -> List[Dict[str, str]]:
    """
    Get all nodes conditions.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    nodes = v1.list_node()

    result = []

    for node in nodes.items:
        n = {"name": node.metadata.name}
        for cond in node.status.conditions:
            n[cond.type] = cond.status
        result.append(n)

    logger.debug(f"Nodes statuses: {result}")

    return result


def all_nodes_must_be_ready_to_schedule(
    configuration: Configuration = None, secrets: Secrets = None
) -> bool:
    """
    Verifies that all nodes in the cluster are in `Ready` condition and can
    be scheduled.
    """
    result = get_all_node_status_conditions(configuration, secrets)

    for statuses in result:
        if statuses.get("Ready") != "True":
            return False

    return True
