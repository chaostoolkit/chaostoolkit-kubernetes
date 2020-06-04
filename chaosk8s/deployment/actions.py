import json
import os.path
import yaml

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger
from kubernetes.client.rest import ApiException

from chaosk8s import create_k8s_api_client

__all__ = ["create_deployment", "delete_deployment", "scale_deployment", "update_image"]


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

    v1 = client.AppsV1beta1Api(api)
    resp = v1.create_namespaced_deployment(ns, body=deployment)


def delete_deployment(name: str, ns: str = "default",
                      label_selector: str = "name in ({name})",
                      secrets: Secrets = None):
    """
    Delete a deployment by `name` in the namespace `ns`.

    The deployment is deleted without a graceful period to trigger an abrupt
    termination.

    The selected resources are matched by the given `label_selector`.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1beta1Api(api)
    if label_selector:
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

    v1 = client.ExtensionsV1beta1Api(api)
    body = {"spec": {"replicas": replicas}}
    try:
        v1.patch_namespaced_deployment_scale(name, namespace=ns, body=body)
    except ApiException as e:
        raise ActivityFailed(
            "failed to scale '{s}' to {r} replicas: {e}".format(
                s=name, r=replicas, e=str(e)))


def update_image(name: str, image: str, ns: "default", container_name: str,
                 secrets: Secrets = None):
    """
    Updates a deployment to use the given container `image`.
    """
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1Api(api)
    deployment = v1.read_namespaced_deployment(name, ns)
    container_found = False
    for container in deployment.spec.template.spec.containers:
        if container.name == container_name:
            container.image = image
            container_found = True
    if not container_found:
        raise ActivityFailed("container with the given name was not found: {}"
                             .format(container_name))
    v1.replace_namespaced_deployment(name, ns, deployment)
