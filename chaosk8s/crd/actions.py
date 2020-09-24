# -*- coding: utf-8 -*-
import json
import os.path
from typing import Any, Dict

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException
from logzero import logger
import yaml

from chaosk8s import create_k8s_api_client

__all__ = ["create_custom_object", "delete_custom_object",
           "create_cluster_custom_object", "delete_cluster_custom_object",
           "patch_custom_object", "replace_custom_object",
           "patch_cluster_custom_object", "replace_cluster_custom_object"]


def create_custom_object(group: str, version: str, plural: str,
                         ns: str = "default",
                         resource: Dict[str, Any] = None,
                         resource_as_yaml_file: str = None,
                         secrets: Secrets = None) -> Dict[str, Any]:
    """
    Create a custom object in the given namespace. Its custom resource
    definition must already exists or this will fail with a 404.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))
    body = load_body(resource, resource_as_yaml_file)

    try:
        r = api.create_namespaced_custom_object(
            group, version, ns, plural, body, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        if x.status == 409:
            logger.debug(
                "Custom resource object {}/{} already exists".format(
                    group, version))
            return json.loads(x.body)
        else:
            raise ActivityFailed(
                "Failed to create custom resource object: '{}' {}".format(
                    x.reason, x.body))


def delete_custom_object(group: str, version: str, plural: str, name: str,
                         ns: str = "default",
                         secrets: Secrets = None) -> Dict[str, Any]:
    """
    Create a custom object cluster wide. Its custom resource
    definition must already exists or this will fail with a 404.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))

    try:
        r = api.delete_namespaced_custom_object(
            group, version, ns, plural, name, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            "Failed to delete custom resource object: '{}' {}".format(
                x.reason, x.body))


def create_cluster_custom_object(group: str, version: str, plural: str,
                                 resource: Dict[str, Any] = None,
                                 resource_as_yaml_file: str = None,
                                 secrets: Secrets = None) -> Dict[str, Any]:
    """
    Delete a custom object in the given namespace.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))
    body = load_body(resource, resource_as_yaml_file)

    try:
        r = api.create_cluster_custom_object(
            group, version, plural, body, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        if x.status == 409:
            logger.debug(
                "Custom resource object {}/{} already exists".format(
                    group, version))
            return json.loads(x.body)
        else:
            raise ActivityFailed(
                "Failed to create custom resource object: '{}' {}".format(
                    x.reason, x.body))


def delete_cluster_custom_object(group: str, version: str, plural: str,
                                 name: str,
                                 secrets: Secrets = None) -> Dict[str, Any]:
    """
    Delete a custom object cluster wide.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))

    try:
        r = api.delete_cluster_custom_object(
            group, version, plural, name, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            "Failed to delete custom resource object: '{}' {}".format(
                x.reason, x.body))


def patch_custom_object(group: str, version: str, plural: str, name: str,
                        ns: str = "default", force: bool = False,
                        resource: Dict[str, Any] = None,
                        resource_as_yaml_file: str = None,
                        secrets: Secrets = None) -> Dict[str, Any]:
    """
    Patch a custom object in the given namespace. The resource must be the
    updated version to apply. Force will re-acquire conflicting fields
    owned by others.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))
    body = load_body(resource, resource_as_yaml_file)

    try:
        r = api.patch_namespaced_custom_object(
            group, version, ns, plural, name, body, force=force,
            _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            "Failed to patch custom resource object: '{}' {}".format(
                x.reason, x.body))


def replace_custom_object(group: str, version: str, plural: str, name: str,
                          ns: str = "default", force: bool = False,
                          resource: Dict[str, Any] = None,
                          resource_as_yaml_file: str = None,
                          secrets: Secrets = None) -> Dict[str, Any]:
    """
    Replace a custom object in the given namespace. The resource must be the
    new version to apply.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))
    body = load_body(resource, resource_as_yaml_file)

    try:
        r = api.replace_namespaced_custom_object(
            group, version, ns, plural, name, body, force=force,
            _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            "Failed to replace custom resource object: '{}' {}".format(
                x.reason, x.body))


def patch_cluster_custom_object(group: str, version: str, plural: str,
                                name: str, force: bool = False,
                                resource: Dict[str, Any] = None,
                                resource_as_yaml_file: str = None,
                                secrets: Secrets = None) -> Dict[str, Any]:
    """
    Patch a custom object cluster-wide. The resource must be the
    updated version to apply. Force will re-acquire conflicting fields
    owned by others.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))
    body = load_body(resource, resource_as_yaml_file)

    try:
        r = api.patch_cluster_custom_object(
            group, version, plural, name, body, force=force,
            _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            "Failed to patch custom resource object: '{}' {}".format(
                x.reason, x.body))


def replace_cluster_custom_object(group: str, version: str, plural: str,
                                  name: str, force: bool = False,
                                  resource: Dict[str, Any] = None,
                                  resource_as_yaml_file: str = None,
                                  secrets: Secrets = None) -> Dict[str, Any]:
    """
    Replace a custom object in the given namespace. The resource must be the
    new version to apply.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))
    body = load_body(resource, resource_as_yaml_file)

    try:
        r = api.replace_cluster_custom_object(
            group, version, plural, name, body, force=force,
            _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            "Failed to replace custom resource object: '{}' {}".format(
                x.reason, x.body))


###############################################################################
# Internal functions
###############################################################################
def load_body(body_as_object: Dict[str, Any] = None,
              body_as_yaml_file: str = None) -> Dict[str, Any]:
    if (body_as_object is None) and (not body_as_yaml_file):
        raise ActivityFailed(
            "Either `body_as_object` or `body_as_yaml_file` must be set")

    if body_as_object is not None:
        return body_as_object

    if not os.path.isfile(body_as_yaml_file):
        raise ActivityFailed(
            "Path '{}' is not a valid resource file".format(body_as_yaml_file))
    else:
        with open(body_as_yaml_file) as f:
            return yaml.safe_load(f.read())
