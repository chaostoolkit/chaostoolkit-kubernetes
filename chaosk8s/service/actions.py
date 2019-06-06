from chaoslib.types import Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = ["delete_service"]


def delete_service(name: str, ns: str = "default", secrets: Secrets = None):
    """
    Remove the given service
    """
    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    v1.delete_namespaced_service(name, namespace=ns)
