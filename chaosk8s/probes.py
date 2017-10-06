# -*- coding: utf-8 -*-
import json
import os.path
from typing import Union

from kubernetes import client, config
import yaml

from chaoslib.exceptions import FailedProbe
from chaoslib.types import MicroservicesStatus

__all__ = ["all_microservices_healthy", "microservice_available_and_healthy",
           "microservice_is_not_available"]


def all_microservices_healthy(ns: str = "default") -> MicroservicesStatus:
    """
    Check all microservices in the system are running and available.

    Raises :exc:`chaoslib.exceptions.FailedProbe` when the state is not
    as expected.
    """
    config.load_kube_config()
    not_ready = []
    failed = []

    v1 = client.CoreV1Api()
    ret = v1.list_namespaced_pod(namespace=ns)
    for p in ret.items:
        phase = p.status.phase
        if phase == "Failed":
            failed.append(p)
        elif phase != "Running":
            not_ready.append(p)

    # we probably should list them in the message
    if failed or not_ready:
        raise FailedProbe("the system is unhealthy")


def microservice_available_and_healthy(
        name: str, ns: str = "default") -> Union[bool, None]:
    """
    Lookup a deployment with a `service` label set to the given `name` in
    the specified `ns`.

    Raises :exc:`chaoslib.exceptions.FailedProbe` when the state is not
    as expected.
    """
    config.load_kube_config()

    v1 = client.AppsV1beta1Api()
    ret = v1.list_namespaced_deployment(
        ns, label_selector="service={name}".format(name=name))

    if not ret.items:
        raise FailedProbe(
            "microservice '{name}' was not found".format(name=name))

    for d in ret.items:
        if d.status.available_replicas != d.spec.replicas:
            raise FailedProbe(
                "microservice '{name}' is not healthy".format(name=name))


def microservice_is_not_available(name: str, ns: str = "default") -> bool:
    """
    Lookup a deployment with a `service` label set to the given `name` in
    the specified `ns`.

    Raises :exc:`chaoslib.exceptions.FailedProbe` when the state is not
    as expected.
    """
    config.load_kube_config()

    v1 = client.AppsV1beta1Api()
    ret = v1.list_namespaced_deployment(
        ns, label_selector="service={name}".format(name=name))

    if ret.items:
        raise FailedProbe(
            "microservice '{name}' looks healthy".format(name=name))
