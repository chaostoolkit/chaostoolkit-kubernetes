import logging
from chaoslib.types import Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = ["secret_exists"]
logger = logging.getLogger("chaostoolkit")


def secret_exists(
    name: str = None,
    ns: str = "default",
    label_selector: str = None,
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a secret by its name and returns False when
    the secret was not found.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    if name and not label_selector:
        logger.debug(f"Filtering secrets by name {name}")
        ret = v1.list_namespaced_secret(
            ns, field_selector=f"metadata.name={name}"
        )
        logger.debug(
            f"Found {len(ret.items)} secrets(s) named '{name}' in ns '{ns}'"
        )
    elif label_selector and not name:
        logger.debug(f"Filtering secrets by label {label_selector}")
        ret = v1.list_namespaced_secret(ns, label_selector=label_selector)
        logger.debug(
            f"Found {len(ret.items)} secret(s) in ns '{ns}'"
            " labelled '{label_selector}'"
        )
    elif name and label_selector:
        logger.debug(
            f"Filtering secrets by name {name} and label {label_selector}"
        )
        ret = v1.list_namespaced_secret(
            ns,
            field_selector=f"metadata.name={name}",
            label_selector=label_selector,
        )
        logger.debug(
            f"Found {len(ret.items)} secret(s) named '{name}' and labelled"
            f" '{label_selector}' in ns '{ns}'"
        )
    else:
        ret = v1.list_namespaced_secret(ns)
        logger.debug(f"Found {len(ret.items)} secret(s) in ns '{ns}'")

    if not ret.items:
        m = f"secret '{name}' does not exist"
        logger.debug(m)
        return False

    return True
