
# -*- coding: utf-8 -*-
import json
import os.path
from typing import Union

from chaoslib.exceptions import FailedProbe
from chaoslib.types import MicroservicesStatus, Secrets
from kubernetes import client
import yaml

from chaosk8s import create_k8s_api_client


__all__ = ["start_microservice", "kill_microservice",
           "remove_service_endpoint"]


def start_microservice(spec_path: str, ns: str = "default",
                       secrets: Secrets = None):
    """
    Start a microservice described by the deployment config, which must be the
    path to the JSON or YAML representation of the deployment.
    """
    api = create_k8s_api_client()

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == '.json':
            deployment = json.loads(f.read())
        elif ext in ['.yml', '.yaml']:
            deployment = yaml.load(f.read())
        else:
            raise FailedProbe(
                "cannot process {path}".format(path=spec_path))

    v1 = client.AppsV1beta1Api(api)
    resp = v1.create_namespaced_deployment(ns, body=deployment)
    return resp


def kill_microservice(name: str, ns: str = "default",
                      secrets: Secrets = None):
    """
    Kill a microservice by `name` in the namespace `ns`.

    The microservice is killed by deleting the deployment for it without
    a graceful period to trigger an abrupt termination.

    To work, the deployment must have a `service` label matching the
    `name` of the microservice.
    """
    api = create_k8s_api_client()

    v1 = client.AppsV1beta1Api(api)
    ret = v1.list_namespaced_deployment(
        ns, label_selector="service={name}".format(name=name))

    body = client.V1DeleteOptions(api)
    for d in ret.items:
        res = v1.delete_namespaced_deployment(
            d.metadata.name, ns, body)

    v1 = client.ExtensionsV1beta1Api(client)
    ret = v1.list_namespaced_replica_set(
        ns, label_selector="service={name}".format(name=name))

    body = client.V1DeleteOptions(api)
    for r in ret.items:
        res = v1.delete_namespaced_replica_set(
            r.metadata.name, ns, body)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(
        ns, label_selector="service={name}".format(name=name))

    body = client.V1DeleteOptions(api)
    for p in ret.items:
        res = v1.delete_namespaced_pod(
            p.metadata.name, ns, body)


def remove_service_endpoint(name: str, ns: str = "default",
                            secrets: Secrets = None):
    """
    Remove the service endpoint that sits in front of microservices (pods).
    """
    api = create_k8s_api_client()

    v1 = client.CoreV1Api(api)
    v1.delete_namespaced_service(name, namespace=ns)
