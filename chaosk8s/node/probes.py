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
    "verify_nodes_condition",
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
    label_selector: str = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> List[Dict[str, str]]:
    """
    Get all nodes conditions. You can select a subset of nodes by specifying a
    `label_selector`.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    nodes = v1.list_node(label_selector=label_selector or None)

    result = []

    for node in nodes.items:
        n = {"name": node.metadata.name}
        for cond in node.status.conditions:
            n[cond.type] = cond.status
        result.append(n)

    logger.debug(f"Nodes statuses: {result}")

    return result


def all_nodes_must_be_ready_to_schedule(
    label_selector: str = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> bool:
    """
    Verifies that all nodes in the cluster are in `Ready` condition and can
    be scheduled. You can select a subset of nodes by specifying a
    `label_selector`.
    """
    result = get_all_node_status_conditions(
        label_selector, configuration, secrets
    )

    for statuses in result:
        if statuses.get("Ready") != "True":
            logger.debug(f"Node {statuses['name']} is not in 'Ready' state")
            return False

    return True


def verify_nodes_condition(
    condition_type: str = "PIDPressure",
    condition_value: str = "False",
    label_selector: str = None,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> bool:
    """
    For each select node, verifies that the gievn condition is met.
    """
    result = get_all_node_status_conditions(
        label_selector, configuration, secrets
    )

    for statuses in result:
        if statuses.get(condition_type) != condition_value:
            logger.debug(
                f"Node {statuses['name']} does not match '{condition_type}' "
                "expected state"
            )
            return False

    return True
