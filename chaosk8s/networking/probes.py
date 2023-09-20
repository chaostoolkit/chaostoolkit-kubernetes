from chaoslib.types import Secrets
from kubernetes import client
from logzero import logger

from chaosk8s import create_k8s_api_client

__all__ = ["ingress_exists"]


def ingress_exists(
    name: str,
    ns: str = "default",
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a ingress by its name and returns False when
    the ingress was not found.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.NetworkingV1Api(api)

    ret = v1.list_namespaced_ingress(
        namespace=ns, field_selector=f"metadata.name={name}"
    )

    if not ret.items:
        logger.debug(f"ingress '{name}' does not exist")
        return False

    return True
