import json
from typing import Any, Dict, List

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException

from chaosk8s import create_k8s_api_client

__all__ = [
    "get_custom_object",
    "get_cluster_custom_object",
    "list_custom_objects",
    "list_cluster_custom_objects",
]


def get_custom_object(
    group: str,
    version: str,
    plural: str,
    name: str,
    ns: str = "default",
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Get a custom object in the given namespace.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))

    try:
        r = api.get_namespaced_custom_object(
            group, version, ns, plural, name, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            f"Failed to create custom resource object: '{x.reason}' {x.body}"
        )


def list_custom_objects(
    group: str,
    version: str,
    plural: str,
    ns: str = "default",
    secrets: Secrets = None,
) -> List[Dict[str, Any]]:
    """
    List custom objects in the given namespace.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))

    try:
        r = api.list_namespaced_custom_object(
            group, version, ns, plural, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            f"Failed to create custom resource object: '{x.reason}' {x.body}"
        )


def get_cluster_custom_object(
    group: str, version: str, plural: str, name: str, secrets: Secrets = None
) -> Dict[str, Any]:
    """
    Get a custom object cluster-wide.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))

    try:
        r = api.get_cluster_custom_object(
            group, version, plural, name, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            f"Failed to create custom resource object: '{x.reason}' {x.body}"
        )


def list_cluster_custom_objects(
    group: str, version: str, plural: str, secrets: Secrets = None
) -> List[Dict[str, Any]]:
    """
    List custom objects cluster-wide.

    Read more about custom resources here:
    https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
    """  # noqa: E501
    api = client.CustomObjectsApi(create_k8s_api_client(secrets))

    try:
        r = api.list_cluster_custom_object(
            group, version, plural, _preload_content=False
        )
        return json.loads(r.data)
    except ApiException as x:
        raise ActivityFailed(
            f"Failed to create custom resource object: '{x.reason}' {x.body}"
        )
