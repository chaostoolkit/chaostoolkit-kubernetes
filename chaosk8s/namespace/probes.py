from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["namespace_exists"]


def namespace_exists(
    name: str,
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a namespace by its name and returns False when
    the namespace was not found.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    ret = v1.list_namespace(field_selector=f"metadata.name={name}")

    if not ret.items:
        m = f"namespace '{name}' does not exist"
        logger.debug(m)
        return False

    return True
