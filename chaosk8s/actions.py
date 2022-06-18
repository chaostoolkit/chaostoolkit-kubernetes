from chaoslib.types import Secrets

from chaosk8s import _log_deprecated
from chaosk8s.deployment.actions import (
    create_deployment,
    delete_deployment,
    scale_deployment,
)
from chaosk8s.pod.actions import delete_pods
from chaosk8s.replicaset.actions import delete_replica_set
from chaosk8s.service.actions import delete_service

__all__ = [
    "start_microservice",
    "kill_microservice",
    "scale_microservice",
    "remove_service_endpoint",
]


def start_microservice(spec_path: str, ns: str = "default", secrets: Secrets = None):
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated("start_microservice", "create_deployment")
    create_deployment(spec_path, ns, secrets)


def remove_service_endpoint(name: str, ns: str = "default", secrets: Secrets = None):
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated("remove_service_endpoint", "delete_service")
    delete_service(name, ns, secrets)


def scale_microservice(
    name: str, replicas: int, ns: str = "default", secrets: Secrets = None
):
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated("scale_microserviceal", "scale_deployment")
    scale_deployment(name, replicas, ns, secrets)


def kill_microservice(
    name: str,
    ns: str = "default",
    label_selector: str = "name in ({name})",
    secrets: Secrets = None,
):
    """
    !!!DEPRECATED!!!
    """
    _log_deprecated(
        "kill_microservice", "delete_deployment/delete_replica_set/delete_pods"
    )
    delete_deployment(name, ns, label_selector, secrets)
    delete_replica_set(name, ns, label_selector, secrets)
    delete_pods(name, ns, label_selector, secrets)
