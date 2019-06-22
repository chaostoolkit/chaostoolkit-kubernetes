# -*- coding: utf-8 -*-
# WARNING: This module exposes actions that have rather strong impacts on your
# cluster. While Chaos Engineering is all about disrupting and weaknesses,
# it is important to take the time to fully appreciate what those actions
# do and how they do it.
import random
import time
from typing import Any, Dict

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["create_node", "delete_nodes", "cordon_node", "drain_nodes",
           "uncordon_node"]


def delete_nodes(label_selector: str = None, all: bool = False,
                 rand: bool = False, count: int = None,
                 grace_period_seconds: int = None, secrets: Secrets = None):
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
    if label_selector:
        ret = v1.list_node(label_selector=label_selector)
        logger.debug("Found {d} nodes labelled '{s}'".format(
            d=len(ret.items), s=label_selector))
    else:
        ret = v1.list_node()
        logger.debug("Found {d} nodes".format(d=len(ret.items)))

    nodes = ret.items
    if not nodes:
        raise ActivityFailed(
            "failed to find a node that matches selector {}".format(
                label_selector))

    if rand:
        nodes = [random.choice(nodes)]
        logger.debug("Picked node '{p}' to be terminated".format(
            p=nodes[0].metadata.name))
    elif count is not None:
        nodes = random.choices(nodes, k=count)
        logger.debug("Picked {c} nodes '{p}' to be terminated".format(
            c=len(nodes), p=", ".join([n.metadata.name for n in nodes])))
    elif not all:
        nodes = [nodes[0]]
        logger.debug("Picked node '{p}' to be terminated".format(
            p=nodes[0].metadata.name))
    else:
        logger.debug("Picked all nodes '{p}' to be terminated".format(
            p=", ".join([n.metadata.name for n in nodes])))

    body = client.V1DeleteOptions()
    for n in nodes:
        res = v1.delete_node(
            n.metadata.name,
            body=body,
            grace_period_seconds=grace_period_seconds)

        if res.status != "Success":
            logger.debug("Terminating nodes failed: {}".format(res.message))


def create_node(meta: Dict[str, Any] = None, spec: Dict[str, Any] = None,
                secrets: Secrets = None) -> client.V1Node:
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
        raise ActivityFailed("Creating new node failed: {}".format(x.body))

    logger.debug("Node '{}' created".format(res.metadata.name))

    return res


def cordon_node(name: str = None, label_selector: str = None,
                secrets: Secrets = None):
    """
    Cordon nodes matching the given label or name, so that no pods
    are scheduled on them any longer.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if name:
        ret = v1.list_node(field_selector="metadata.name={}".format(name))
        logger.debug("Found {d} node named '{s}'".format(
            d=len(ret.items), s=name))
    elif label_selector:
        ret = v1.list_node(label_selector=label_selector)
        logger.debug("Found {d} node(s) labelled '{s}'".format(
            d=len(ret.items), s=label_selector))
    else:
        ret = v1.list_node()
        logger.debug("Found {d} node(s)".format(d=len(ret.items)))

    nodes = ret.items
    if not nodes:
        raise ActivityFailed(
            "failed to find a node that matches selector {}".format(
                label_selector))

    body = {
        "spec": {
            "unschedulable": True
        }
    }

    for n in nodes:
        try:
            v1.patch_node(n.metadata.name, body)
        except ApiException as x:
            logger.debug("Unscheduling node '{}' failed: {}".format(
                n.metadata.name, x.body))
            raise ActivityFailed("Failed to unschedule node '{}': {}".format(
                n.metadata.name, x.body))


def uncordon_node(name: str = None, label_selector: str = None,
                  secrets: Secrets = None):
    """
    Uncordon nodes matching the given label name, so that pods can be
    scheduled on them again.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if name:
        ret = v1.list_node(field_selector="metadata.name={}".format(name))
        logger.debug("Found {d} node named '{s}'".format(
            d=len(ret.items), s=name))
    elif label_selector:
        ret = v1.list_node(label_selector=label_selector)
        logger.debug("Found {d} node(s) labelled '{s}'".format(
            d=len(ret.items), s=label_selector))
    else:
        ret = v1.list_node()
        logger.debug("Found {d} node(s)".format(d=len(ret.items)))

    nodes = ret.items
    if not nodes:
        raise ActivityFailed(
            "failed to find a node that matches selector {}".format(
                label_selector))

    body = {
        "spec": {
            "unschedulable": False
        }
    }

    for n in nodes:
        try:
            v1.patch_node(n.metadata.name, body)
        except ApiException as x:
            logger.debug("Scheduling node '{}' failed: {}".format(
                n.metadata.name, x.body))
            raise ActivityFailed("Failed to schedule node '{}': {}".format(
                n.metadata.name, x.body))


def drain_nodes(name: str = None, label_selector: str = None,
                delete_pods_with_local_storage: bool = False,
                timeout: int = 120, secrets: Secrets = None) -> bool:
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
    cordon_node(name=name, label_selector=label_selector, secrets=secrets)

    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if name:
        ret = v1.list_node(field_selector="metadata.name={}".format(name))
        logger.debug("Found {d} node named '{s}'".format(
            d=len(ret.items), s=name))
    elif label_selector:
        ret = v1.list_node(label_selector=label_selector)
        logger.debug("Found {d} node(s) labelled '{s}'".format(
            d=len(ret.items), s=label_selector))
    else:
        ret = v1.list_node()
        logger.debug("Found {d} node(s)".format(d=len(ret.items)))

    nodes = ret.items
    if not nodes:
        raise ActivityFailed(
            "failed to find a node that matches selector {}".format(
                label_selector))

    for node in nodes:
        node_name = node.metadata.name
        ret = v1.list_pod_for_all_namespaces(
            include_uninitialized=True,
            field_selector="spec.nodeName={}".format(node_name))

        logger.debug("Found {d} pods on node '{n}'".format(
            d=len(ret.items), n=node_name))

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
                logger.debug("Not deleting mirror pod '{}' on "
                             "node '{}'".format(name, node_name))
                continue

            if any(filter(lambda v: v.empty_dir is not None, volumes)):
                logger.debug(
                    "Pod '{}' on node '{}' has a volume made "
                    "of a local storage".format(name, node_name))
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
                        "Pod '{}' on node '{}' is owned by a DaemonSet. Will "
                        "not evict it".format(name, node_name))
                    break
            else:
                raise ActivityFailed(
                    "Pod '{}' on node '{}' is unmanaged, cannot drain this "
                    "node. Delete it manually first?".format(name, node_name))

        if not eviction_candidates:
            logger.debug("No pods to evict. Let's return.")
            return True

        logger.debug("Found {} pods to evict".format(len(eviction_candidates)))
        for pod in eviction_candidates:
            eviction = client.V1beta1Eviction()

            eviction.metadata = client.V1ObjectMeta()
            eviction.metadata.name = pod.metadata.name
            eviction.metadata.namespace = pod.metadata.namespace

            eviction.delete_options = client.V1DeleteOptions()
            try:
                v1.create_namespaced_pod_eviction(
                    pod.metadata.name, pod.metadata.namespace, body=eviction)
            except ApiException as x:
                raise ActivityFailed(
                    "Failed to evict pod {}: {}".format(
                        pod.metadata.name, x.body))

        pods = eviction_candidates[:]
        started = time.time()
        while True:
            logger.debug("Waiting for {} pods to go".format(len(pods)))

            if time.time() - started > timeout:
                remaining_pods = "\n".join([p.metadata.name for p in pods])
                raise ActivityFailed(
                    "Draining nodes did not completed within {}s. "
                    "Remaining pods are:\n{}".format(timeout, remaining_pods))

            pending_pods = pods[:]
            for pod in pods:
                try:
                    p = v1.read_namespaced_pod(
                        pod.metadata.name, pod.metadata.namespace)
                    # rescheduled elsewhere?
                    if p.metadata.uid != pod.metadata.uid:
                        pending_pods.remove(pod)
                        continue
                    logger.debug("Pod '{}' still around in phase: {}".format(
                        p.metadata.name, p.status.phase))
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
