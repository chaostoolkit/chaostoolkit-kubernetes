# -*- coding: utf-8 -*-
import json
import os.path
from typing import Union

from chaoslib.exceptions import FailedActivity
from chaoslib.types import MicroservicesStatus, Secrets
from kubernetes import client
import yaml

from chaosk8s import create_k8s_api_client


__all__ = ["all_microservices_healthy", "microservice_available_and_healthy",
           "microservice_is_not_available", "service_endpoint_is_initialized"]


def all_microservices_healthy(ns: str = "default",
                              secrets: Secrets = None) -> MicroservicesStatus:
    """
    Check all microservices in the system are running and available.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)
    not_ready = []
    failed = []

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(namespace=ns)
    for p in ret.items:
        phase = p.status.phase
        if phase == "Failed":
            failed.append(p)
        elif phase != "Running":
            not_ready.append(p)

    # we probably should list them in the message
    if failed or not_ready:
        raise FailedActivity("the system is unhealthy")

    return True


def microservice_available_and_healthy(
        name: str, ns: str = "default",
        secrets: Secrets = None) -> Union[bool, None]:
    """
    Lookup a deployment with a `service` label set to the given `name` in
    the specified `ns`.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1beta1Api(api)
    ret = v1.list_namespaced_deployment(
        ns, label_selector="service={name}".format(name=name))

    if not ret.items:
        raise FailedActivity(
            "microservice '{name}' was not found".format(name=name))

    for d in ret.items:
        if d.status.available_replicas != d.spec.replicas:
            raise FailedActivity(
                "microservice '{name}' is not healthy".format(name=name))

    return True


def microservice_is_not_available(name: str, ns: str = "default",
                                  secrets: Secrets = None) -> bool:
    """
    Lookup a deployment with a `service` label set to the given `name` in
    the specified `ns`.

    Raises :exc:`chaoslib.exceptions.FailedProbe` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1beta1Api(api)
    ret = v1.list_namespaced_deployment(
        ns, label_selector="service={name}".format(name=name))

    if ret.items:
        raise FailedActivity(
            "microservice '{name}' looks healthy".format(name=name))

    return True


def service_endpoint_is_initialized(name: str, ns: str= "default",
                                    secrets: Secrets = None):
    """
    Lookup a service endpoint by its name and raises :exc:`FailedProbe` when
    the service was not found or not initialized.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_service(
        ns, label_selector="service={name}".format(name=name))

    if not ret.items:
        raise FailedActivity(
            "service '{name}' is not initialized".format(name=name))

    return True
