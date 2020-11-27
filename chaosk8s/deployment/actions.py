import json
import os.path
import yaml

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger
from kubernetes.client.rest import ApiException

from chaosk8s import create_k8s_api_client

__all__ = ["create_deployment", "delete_deployment", "scale_deployment"]


def create_deployment(spec_path: str, ns: str = "default",
                      secrets: Secrets = None):
    """
    Create a deployment described by the deployment config, which must be the
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


def delete_deployment(name: str = None, ns: str = "default",
                      label_selector: str = None, secrets: Secrets = None):
    """
    Delete a deployment by `name` or `label_selector` in the namespace `ns`.

    The deployment is deleted without a graceful period to trigger an abrupt
    termination.

    If neither `name` nor `label_selector` is specified, all the deployments
    will be deleted in the namespace.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)

    if name:
        ret = v1.list_namespaced_deployment(
            ns, field_selector="metadata.name={}".format(name))
    elif label_selector:
        ret = v1.list_namespaced_deployment(ns, label_selector=label_selector)
    else:
        ret = v1.list_namespaced_deployment(ns)

    logger.debug("Found {d} deployments named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for d in ret.items:
        v1.delete_namespaced_deployment(d.metadata.name, ns, body=body)


def scale_deployment(name: str, replicas: int, ns: str = "default",
                     secrets: Secrets = None):
    """
    Scale a deployment up or down. The `name` is the name of the deployment.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1Api(api)
    body = {"spec": {"replicas": replicas}}
    try:
        v1.patch_namespaced_deployment(name=name, namespace=ns, body=body)
    except ApiException as e:
        raise ActivityFailed(
            "failed to scale '{s}' to {r} replicas: {e}".format(
                s=name, r=replicas, e=str(e)))
