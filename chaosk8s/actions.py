
# -*- coding: utf-8 -*-
import json
import os.path
from typing import Union

from kubernetes import client, config
import yaml

from chaoslib.exceptions import FailedProbe
from chaoslib.types import MicroservicesStatus

__all__ = ["start_microservice", "kill_microservice"]


def start_microservice(spec_path: str, ns: str = "default"):
    """
    Start a microservice described by the deployment config, which must be the
    path to the JSON or YAML representation of the deployment.
    """
    config.load_kube_config()

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == '.json':
            deployment = json.loads(f.read())
        elif ext in ['.yml', '.yaml']:
            deployment = yaml.load(f.read())
        else:
            raise FailedProbe(
                "cannot process {path}".format(path=spec_path))

    v1 = client.AppsV1beta1Api()
    resp = v1.create_namespaced_deployment(ns, body=deployment)
    return resp


def kill_microservice(name: str, ns: str = "default"):
    """
    Kill a microservice by `name` in the namespace `ns`.

    The microservice is killed by deleting the deployment for it without
    a graceful period to trigger an abrupt termination.

    To work, the deployment must have a `service` label matching the
    `name` of the microservice.
    """
    config.load_kube_config()

    v1 = client.AppsV1beta1Api()
    ret = v1.list_namespaced_deployment(
        ns, label_selector="service={name}".format(name=name))

    body = client.V1DeleteOptions()
    for d in ret.items:
        res = v1.delete_namespaced_deployment(
            d.metadata.name, ns, body)

    v1 = client.ExtensionsV1beta1Api()
    ret = v1.list_namespaced_replica_set(
        ns, label_selector="service={name}".format(name=name))

    body = client.V1DeleteOptions()
    for r in ret.items:
        res = v1.delete_namespaced_replica_set(
            r.metadata.name, ns, body)

    v1 = client.CoreV1Api()
    ret = v1.list_namespaced_pod(
        ns, label_selector="service={name}".format(name=name))

    body = client.V1DeleteOptions()
    for p in ret.items:
        res = v1.delete_namespaced_pod(
            p.metadata.name, ns, body)
