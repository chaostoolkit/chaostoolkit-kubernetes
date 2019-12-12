# -*- coding: utf-8 -*-
import json
import os.path

import yaml
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["start_microservice", "kill_microservice", "scale_microservice",
           "remove_service_endpoint"]


def start_microservice(spec_path: str, ns: str = "default",
                       secrets: Secrets = None):
    """
    Start a microservice described by the deployment config, which must be the
    path to the JSON or YAML representation of the deployment.
    """
    api = create_k8s_api_client(secrets)

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == '.json':
            deployment = json.loads(f.read())
        elif ext in ['.yml', '.yaml']:
            deployment = yaml.load(f.read())
        else:
            raise ActivityFailed(
                "cannot process {path}".format(path=spec_path))

    v1 = client.AppsV1Api(api)
    resp = v1.create_namespaced_deployment(ns, body=deployment)
    return resp


def kill_microservice(name: str, ns: str = "default",
                      label_selector: str = "name in ({name})",
                      secrets: Secrets = None):
    """
    Kill a microservice by `name` in the namespace `ns`.

    The microservice is killed by deleting the deployment for it without
    a graceful period to trigger an abrupt termination.

    The selected resources are matched by the given `label_selector`.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_deployment(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_deployment(ns)

    logger.debug("Found {d} deployments named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for d in ret.items:
        res = v1.delete_namespaced_deployment(
            d.metadata.name, ns, body=body)

    v1 = client.AppsV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_replica_set(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_replica_set(ns)

    logger.debug("Found {d} replica sets named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for r in ret.items:
        res = v1.delete_namespaced_replica_set(
            r.metadata.name, ns, body=body)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_namespaced_pod(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_pod(ns)

    logger.debug("Found {d} pods named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for p in ret.items:
        res = v1.delete_namespaced_pod(
            p.metadata.name, ns, body=body)


def remove_service_endpoint(name: str, ns: str = "default",
                            secrets: Secrets = None):
    """
    Remove the service endpoint that sits in front of microservices (pods).
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    v1.delete_namespaced_service(name, namespace=ns)


def scale_microservice(name: str, replicas: int, ns: str = "default",
                       secrets: Secrets = None):
    """
    Scale a deployment up or down. The `name` is the name of the deployment.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    body = {"spec": {"replicas": replicas}}
    try:
        v1.patch_namespaced_deployment_scale(name, namespace=ns, body=body)
    except ApiException as e:
        raise ActivityFailed(
            "failed to scale '{s}' to {r} replicas: {e}".format(
                s=name, r=replicas, e=str(e)))
