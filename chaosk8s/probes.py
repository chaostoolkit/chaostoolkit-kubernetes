# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os.path
from typing import Dict, Union
import urllib3

from chaoslib.exceptions import FailedActivity
from chaoslib.types import MicroservicesStatus, Secrets
import dateparser
from logzero import logger
from kubernetes import client, watch
import yaml

from chaosk8s import create_k8s_api_client


__all__ = ["all_microservices_healthy", "microservice_available_and_healthy",
           "microservice_is_not_available", "service_endpoint_is_initialized",
           "deployment_is_not_fully_available", "read_microservices_logs"]


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

    logger.debug("Found {d} failed and {n} not ready pods".format(
        d=len(failed), n=len(not_ready)))

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
        ns, label_selector="name in ({name})".format(name=name))

    logger.debug("Found {d} deployments named '{n}'".format(
        d=len(ret.items), n=name))

    if not ret.items:
        raise FailedActivity(
            "microservice '{name}' was not found".format(name=name))

    for d in ret.items:
        logger.debug("Deployment has '{s}' available replicas".format(
            s=d.status.available_replicas))

        if d.status.available_replicas != d.spec.replicas:
            raise FailedActivity(
                "microservice '{name}' is not healthy".format(name=name))

    return True


def microservice_is_not_available(name: str, ns: str = "default",
                                  secrets: Secrets = None) -> bool:
    """
    Lookup pods with a `name` label set to the given `name` in the specified
    `ns`.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when one of the pods
    with the specified `name` is in the `"Running"` phase.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(
        ns, label_selector="name  in ({name})".format(name=name))

    logger.debug("Found {d} pod named '{n}'".format(
        d=len(ret.items), n=name))

    for p in ret.items:
        phase = p.status.phase
        logger.debug("Pod '{p}' has status '{s}'".format(
            p=p.metadata.name, s=phase))
        if phase == "Running":
            raise FailedActivity(
                "microservice '{name}' is actually running".format(name=name))

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
        ns, label_selector="name in ({name})".format(name=name))

    logger.debug("Found {d} services named '{n}'".format(
        d=len(ret.items), n=name))

    if not ret.items:
        raise FailedActivity(
            "service '{name}' is not initialized".format(name=name))

    return True


def deployment_is_not_fully_available(name: str, ns: str= "default",
                                      timeout: int = 30,
                                      secrets: Secrets = None):
    """
    Wait until the deployment gets into an intermediate state where not all
    expected replicas are available. Once this state is reached, return `True`.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.FailedActivity` exception is raised.
    """
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1beta1Api(api)
    w = watch.Watch()
    timeout = int(timeout)

    try:
        logger.debug("Watching events for {t}s".format(t=timeout))
        for event in w.stream(v1.list_namespaced_deployment, namespace=ns,
                              label_selector="name  in ({name})".format(
                                  name=name), _request_timeout=timeout):
            deployment = event['object']
            status = deployment.status
            spec = deployment.spec

            logger.debug(
                "Deployment '{p}' {t}: "
                "Ready Replicas {r} - "
                "Unavailable Replicas {u} - "
                "Desired Replicas {a}".format(
                    p=deployment.metadata.name, t=event["type"],
                    r=status.ready_replicas,
                    a=spec.replicas,
                    u=status.unavailable_replicas))

            if status.ready_replicas != spec.replicas:
                w.stop()
                return True

    except urllib3.exceptions.ReadTimeoutError:
        logger.debug("Timed out!")
        raise FailedActivity(
            "microservice '{name}' failed to stop running within {t}s".format(
                name=name, t=timeout))


def read_microservices_logs(name: str, last: Union[str, None] = None,
                            ns: str="default", with_previous: bool=False,
                            secrets: Secrets=None) -> Dict[str, str]:
    """
    Fetch logs for all the pods with the label `"name"` set to `name` and
    return a dictionnary with the keys being the pod's name and the values
    the logs of said pod.

    If you provide `last`, this returns the logs of the last N seconds
    until now. This can set to a fluent delta such as `10 minutes`.

    You may also set `with_previous` to `True` to capture the logs of a
    previous pod's incarnation, if any.
    """
    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(
        ns, label_selector="name  in ({name})".format(name=name))

    logger.debug("Found {d} pods: [{p}]".format(
        d=len(ret.items), p=', '.join([p.metadata.name for p in ret.items])))

    since = None
    if last:
        now = datetime.now()
        since = int((now - dateparser.parse(last)).total_seconds())

    params = dict(
        namespace=ns,
        follow=False,
        timestamps=True,
        _preload_content=False
    )

    if since:
        params["since_seconds"] = since

    logs = {}
    for p in ret.items:
        name = p.metadata.name
        logger.debug("Fetching logs for pod '{n}'".format(n=name))
        r = v1.read_namespaced_pod_log(name, **params)
        logs[name] = r.read().decode('utf-8')

    return logs
