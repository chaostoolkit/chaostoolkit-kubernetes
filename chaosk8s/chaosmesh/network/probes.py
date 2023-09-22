from typing import Any, Dict

from chaoslib.types import Secrets

from chaosk8s.crd.probes import get_custom_object, list_custom_objects

__all__ = [
    "get_network_fault",
    "get_network_faults",
]


def get_network_faults(
    ns: str = "default",
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    List all Chaos Mesh network faults.
    """

    return list_custom_objects(
        "chaos-mesh.org",
        "v1alpha1",
        "networkchaos",
        ns,
        secrets=secrets,
    )


def get_network_fault(
    name: str,
    ns: str = "default",
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Get a specific Chaos Mesh network fault.
    """

    return get_custom_object(
        "chaos-mesh.org",
        "v1alpha1",
        "networkchaos",
        name,
        ns,
        secrets=secrets,
    )
