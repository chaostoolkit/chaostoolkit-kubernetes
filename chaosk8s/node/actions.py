# WARNING: This module exposes actions that have rather strong impacts on your
# cluster. While Chaos Engineering is all about disrupting and weaknesses,
# it is important to take the time to fully appreciate what those actions
# do and how they do it.
import random
import time
from typing import Any, Dict, List

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["create_node", "delete_nodes", "cordon_node", "drain_nodes", "uncordon_node"]


def _select_nodes(
    name: str = None,
    label_selector: str = None,
    count: int = None,
    secrets: Secrets = None,
    pod_label_selector: str = None,
    pod_namespace: str = None,
    first: bool = False,
) -> List[client.V1Node]:
    """
    Selects nodes of the kubernetes cluster based on the input parameters and
     returns them.
    If no input parameter is given, all nodes are returned.
    In case that no node can be found or matches the filter paramter an
     exception is thrown.

    Nodes can be filtered by their name through the `name` paramteter.
    Nodes can be filtered by their label through the `label_selector`
    parameter.
    Nodes can further be filtered by the pods that they are accommodating using
    the pod's label through the `pod_label_selector` parameter and
    `pod_namespace` parameter.
    The amount of nodes to return can be capped through the `count` paramteter.
    In this case `count` random nodes will be returned.
    If first is set to true only the first node is returned.
    """
    nodes = []
    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)

    if name and not label_selector:
        logger.debug(f"Filtering nodes by name {name}")
        ret = v1.list_node(field_selector=f"metadata.name={name}")
        logger.debug(f"Found {len(ret.items)} nodes")
    elif label_selector and not name:
        logger.debug(f"Filtering nodes by label {label_selector}")
        ret = v1.list_node(label_selector=label_selector)
        logger.debug(f"Found {len(ret.items)} nodes")
    elif name and label_selector:
        logger.debug(
            "Filtering nodes by name %s and \
                      label %s"
            % (name, label_selector)
        )
        ret = v1.list_node(
            field_selector=f"metadata.name={name}",
            label_selector=label_selector,
        )
        logger.debug(f"Found {len(ret.items)} nodes")
    else:
        ret = v1.list_node()

    if pod_label_selector and pod_namespace:
        logger.debug(f"Filtering nodes by pod label {pod_label_selector}")
        pods = v1.list_namespaced_pod(pod_namespace, label_selector=pod_label_selector)
        for node in ret.items:
            for pod in pods.items:
                if pod.spec.node_name == node.metadata.name:
                    nodes.append(node)
                    pass
        logger.debug(f"Found {len(nodes)} nodes")
    else:
        nodes = ret.items

    if not nodes:
        raise ActivityFailed("failed to find a node that matches selector")

    if first:
        nodes = [nodes[0]]
    elif count is not None:
        nodes = random.choices(nodes, k=count)
    logger.debug(f"Picked nodes '{', '.join([n.metadata.name for n in nodes])}'")

    return nodes


def delete_nodes(
    label_selector: str = None,
    all: bool = False,
    rand: bool = False,
    count: int = None,
    grace_period_seconds: int = None,
    secrets: Secrets = None,
    pod_label_selector: str = None,
    pod_namespace: str = None,
):
    """
    Delete nodes gracefully. Select the appropriate nodes by label.

    Nodes are not drained beforehand so we can see how cluster behaves. Nodes
    cannot be restarted, they are really deleted. Please be careful when using
    this action.

    On certain cloud providers, you also need to delete the underneath VM
    instance as well afterwards. This is the case on GCE for instance.

    If `all` is set to `True`, all nodes will be terminated.
    If `rand` is set to `True`, one random node will be terminated.
    If ̀`count` is set to a positive number, only a upto `count` nodes
    (randomly picked) will be terminated. Otherwise, the first retrieved node
    will be terminated.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    first = False
    if (
        (all is None or all is False)
        and (rand is None or rand is False)
        and (count is None or count < 1)
    ):
        first = True

    if rand:
        count = 1

    if all:
        count, label_selector, pod_label_selector, pod_namespace = None

    nodes = _select_nodes(
        secrets=secrets,
        label_selector=label_selector,
        pod_label_selector=pod_label_selector,
        pod_namespace=pod_namespace,
        count=count,
        first=first,
    )

    body = client.V1DeleteOptions()
    for n in nodes:
        res = v1.delete_node(
            n.metadata.name, body=body, grace_period_seconds=grace_period_seconds
        )

        if res.status != "Success":
            logger.debug(f"Terminating nodes failed: {res.message}")


def create_node(
    meta: Dict[str, Any] = None, spec: Dict[str, Any] = None, secrets: Secrets = None
) -> client.V1Node:
    """
    Create one new node in the cluster.

    Due to the way things work on certain cloud providers, you won't be able
    to use this meaningfully on them. For instance on GCE, this will likely
    fail.

    See also: https://github.com/kubernetes/community/blob/master/contributors/devel/api-conventions.md#idempotency
    """  # noqa: E501
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    body = client.V1Node()

    body.metadata = client.V1ObjectMeta(**meta) if meta else None
    body.spec = client.V1NodeSpec(**spec) if spec else None

    try:
        res = v1.create_node(body)
    except ApiException as x:
        raise ActivityFailed(f"Creating new node failed: {x.body}")

    logger.debug(f"Node '{res.metadata.name}' created")

    return res


def cordon_node(name: str = None, label_selector: str = None, secrets: Secrets = None):
    """
    Cordon nodes matching the given label or name, so that no pods
    are scheduled on them any longer.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    nodes = _select_nodes(name=name, label_selector=label_selector, secrets=secrets)

    body = {"spec": {"unschedulable": True}}

    for n in nodes:
        try:
            v1.patch_node(n.metadata.name, body)
        except ApiException as x:
            logger.debug(f"Unscheduling node '{n.metadata.name}' failed: {x.body}")
            raise ActivityFailed(
                f"Failed to unschedule node '{n.metadata.name}': {x.body}"
            )


def uncordon_node(
    name: str = None, label_selector: str = None, secrets: Secrets = None
):
    """
    Uncordon nodes matching the given label name, so that pods can be
    scheduled on them again.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    nodes = _select_nodes(name=name, label_selector=label_selector, secrets=secrets)

    body = {"spec": {"unschedulable": False}}

    for n in nodes:
        try:
            v1.patch_node(n.metadata.name, body)
        except ApiException as x:
            logger.debug(f"Scheduling node '{n.metadata.name}' failed: {x.body}")
            raise ActivityFailed(
                f"Failed to schedule node '{n.metadata.name}': {x.body}"
            )


def drain_nodes(
    name: str = None,
    label_selector: str = None,
    delete_pods_with_local_storage: bool = False,
    timeout: int = 120,
    secrets: Secrets = None,
    count: int = None,
    pod_label_selector: str = None,
    pod_namespace: str = None,
) -> bool:
    """
    Drain nodes matching the given label or name, so that no pods are scheduled
    on them any longer and running pods are evicted.

    It does a similar job to `kubectl drain --ignore-daemonsets` or
    `kubectl drain --delete-local-data --ignore-daemonsets` if
    `delete_pods_with_local_storage` is set to `True`. There is no
    equivalent to the `kubectl drain --force` flag.

    You probably want to call `uncordon` from in your experiment's rollbacks.
    """
    # first let's make the node unschedulable
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    # select nodes to drain
    nodes = _select_nodes(
        name=name,
        label_selector=label_selector,
        count=count,
        pod_label_selector=pod_label_selector,
        pod_namespace=pod_namespace,
        secrets=secrets,
    )

    # first let's make the nodes unschedulable
    for node in nodes:
        cordon_node(name=node.metadata.name, secrets=secrets)

    for node in nodes:
        node_name = node.metadata.name
        ret = v1.list_pod_for_all_namespaces(
            field_selector=f"spec.nodeName={node_name}"
        )

        logger.debug(f"Found {len(ret.items)} pods on node '{node_name}'")

        if not ret.items:
            continue

        # following the drain command from kubectl as best as we can
        eviction_candidates = []
        for pod in ret.items:
            name = pod.metadata.name
            phase = pod.status.phase
            volumes = pod.spec.volumes
            annotations = pod.metadata.annotations

            # do not handle mirror pods
            if annotations and "kubernetes.io/config.mirror" in annotations:
                logger.debug(
                    f"Not deleting mirror pod '{name}' on " f"node '{node_name}'"
                )
                continue

            if any(filter(lambda v: v.empty_dir is not None, volumes)):
                logger.debug(
                    f"Pod '{name}' on node '{node_name}' has a volume made "
                    "of a local storage"
                )
                if not delete_pods_with_local_storage:
                    logger.debug("Not evicting a pod with local storage")
                    continue
                logger.debug("Deleting anyway due to flag")
                eviction_candidates.append(pod)
                continue

            if phase in ["Succeeded", "Failed"]:
                eviction_candidates.append(pod)
                continue

            for owner in pod.metadata.owner_references:
                if owner.controller and owner.kind != "DaemonSet":
                    eviction_candidates.append(pod)
                    break
                elif owner.kind == "DaemonSet":
                    logger.debug(
                        f"Pod '{name}' on node '{node_name}' is owned by a DaemonSet."
                        " Will not evict it"
                    )
                    break
            else:
                raise ActivityFailed(
                    f"Pod '{name}' on node '{node_name}' is unmanaged, cannot drain"
                    " this node. Delete it manually first?"
                )

        if not eviction_candidates:
            logger.debug("No pods to evict. Let's return.")
            return True

        logger.debug(f"Found {len(eviction_candidates)} pods to evict")
        for pod in eviction_candidates:
            eviction = client.V1Eviction()

            eviction.metadata = client.V1ObjectMeta()
            eviction.metadata.name = pod.metadata.name
            eviction.metadata.namespace = pod.metadata.namespace

            eviction.delete_options = client.V1DeleteOptions()
            try:
                v1.create_namespaced_pod_eviction(
                    pod.metadata.name, pod.metadata.namespace, body=eviction
                )
            except ApiException as x:
                raise ActivityFailed(
                    f"Failed to evict pod {pod.metadata.name}: {x.body}"
                )

        pods = eviction_candidates[:]
        started = time.time()
        while True:
            logger.debug(f"Waiting for {len(pods)} pods to go")

            if time.time() - started > timeout:
                remaining_pods = "\n".join([p.metadata.name for p in pods])
                raise ActivityFailed(
                    f"Draining nodes did not completed within {timeout}s. "
                    f"Remaining pods are:\n{remaining_pods}"
                )

            pending_pods = pods[:]
            for pod in pods:
                try:
                    p = v1.read_namespaced_pod(
                        pod.metadata.name, pod.metadata.namespace
                    )
                    # rescheduled elsewhere?
                    if p.metadata.uid != pod.metadata.uid:
                        pending_pods.remove(pod)
                        continue
                    logger.debug(
                        f"Pod '{p.metadata.name}' still around in phase:"
                        f" {p.status.phase}"
                    )
                except ApiException as x:
                    if x.status == 404:
                        # gone...
                        pending_pods.remove(pod)
            pods = pending_pods[:]
            if not pods:
                logger.debug("Evicted all pods we could")
                break

            time.sleep(10)

        return True
