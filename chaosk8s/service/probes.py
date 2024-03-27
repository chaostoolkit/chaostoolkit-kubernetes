import logging

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = ["service_is_initialized"]
logger = logging.getLogger("chaostoolkit")


def service_is_initialized(
    name: str = None,
    ns: str = "default",
    label_selector: str = None,
    raise_if_service_not_initialized: bool = True,
    secrets: Secrets = None,
) -> bool:
    """
    Lookup a service endpoint by its name and raises :exc:`FailedProbe` when
    the service was not found or not initialized.

    If `raise_if_service_not_initialized` is set to `False` return `False`
    when probe isn't as expected. Otherwise raises
    `chaoslib.exceptions.ActivityFailed`
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    if name and not label_selector:
        logger.debug(f"Filtering services by name {name}")
        ret = v1.list_namespaced_service(
            ns, field_selector=f"metadata.name={name}"
        )
        logger.debug(
            f"Found {len(ret.items)} service(s) named '{name}' in ns '{ns}'"
        )
    elif label_selector and not name:
        logger.debug(f"Filtering services by label {label_selector}")
        ret = v1.list_namespaced_service(ns, label_selector=label_selector)
        logger.debug(
            f"Found {len(ret.items)} service(s) in ns '{ns}'"
            " labelled '{label_selector}'"
        )
    elif name and label_selector:
        logger.debug(
            f"Filtering services by name {name} and label {label_selector}"
        )
        ret = v1.list_namespaced_service(
            ns,
            field_selector=f"metadata.name={name}",
            label_selector=label_selector,
        )
        logger.debug(
            f"Found {len(ret.items)} service(s) named '{name}' and labelled"
            f" '{label_selector}' in ns '{ns}'"
        )
    else:
        ret = v1.list_namespaced_service(ns)
        logger.debug(f"Found {len(ret.items)} service(s) in ns '{ns}'")

    if not ret.items:
        m = f"service '{name}' is not initialized"
        if not raise_if_service_not_initialized:
            logger.debug(m)
            return False
        else:
            raise ActivityFailed(m)

    return True
