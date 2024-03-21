from typing import Union

from chaoslib.types import MicroservicesStatus, Secrets

from chaosk8s import _log_deprecated
from chaosk8s.deployment.probes import (
    deployment_available_and_healthy,
    deployment_fully_available,
    deployment_not_fully_available,
)
from chaosk8s.pod.probes import (
    all_pods_healthy,
    pod_is_not_available,
    read_pod_logs,
)
from chaosk8s.secret.probes import secret_exists
from chaosk8s.service.probes import service_is_initialized

__all__ = [
    "all_microservices_healthy",
    "microservice_available_and_healthy",
    "microservice_is_not_available",
    "service_endpoint_is_initialized",
    "deployment_is_not_fully_available",
    "deployment_is_fully_available",
    "read_microservices_logs",
    "secret_exists",
]


# moved to pod/probes.py
def all_microservices_healthy(
    ns: str = "default", secrets: Secrets = None
) -> MicroservicesStatus:
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated("all_microservices_healthy", "all_pods_healthy")
    return all_pods_healthy(ns, secrets=secrets)


# moved to deployment/probes.py
def microservice_available_and_healthy(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    secrets: Secrets = None,
) -> Union[bool, None]:
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated(
        "microservice_available_and_healthy", "deployment_available_and_healthy"
    )
    deployment_available_and_healthy(name, ns, label_selector, secrets=secrets)


# moved to pod/probes.py
def microservice_is_not_available(
    name: str,
    ns: str = "default",
    label_selector: str = "name in ({name})",
    secrets: Secrets = None,
) -> bool:
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated("microservice_is_not_available", "pod_is_not_available")
    return pod_is_not_available(name, ns, label_selector, secrets=secrets)


# moved to service/probes.py
def service_endpoint_is_initialized(
    name: str,
    ns: str = "default",
    label_selector: str = "name in ({name})",
    secrets: Secrets = None,
):
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated("service_endpoint_is_initialized", "service_is_initialized")
    return service_is_initialized(name, ns, label_selector, secrets=secrets)


# moved to deployment/probes.py
def deployment_is_not_fully_available(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
):
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated(
        "deployment_is_not_fully_available", "deployment_not_fully_available"
    )
    return deployment_not_fully_available(
        name, ns, label_selector, timeout, secrets=secrets
    )


# moved to deployment/probes.py
def deployment_is_fully_available(
    name: str,
    ns: str = "default",
    label_selector: str = None,
    timeout: int = 30,
    secrets: Secrets = None,
):
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated(
        "deployment_is_fully_available", "deployment_fully_available"
    )
    return deployment_fully_available(
        name, ns, label_selector, timeout, secrets=secrets
    )


# moved to pod/probes.py
read_microservices_logs = read_pod_logs
