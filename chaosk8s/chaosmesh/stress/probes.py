from typing import Any, Dict

from chaoslib.types import Secrets

from chaosk8s.crd.probes import get_custom_object, list_custom_objects

__all__ = [
    "get_stressor",
    "get_stressors",
]


def get_stressors(
    ns: str = "default",
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    List all Chaos Mesh network CPU/memory stressors.
    """

    return list_custom_objects(
        "chaos-mesh.org",
        "v1alpha1",
        "stresschaos",
        ns,
        secrets=secrets,
    )


def get_stressor(
    name: str,
    ns: str = "default",
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Get a specific Chaos Mesh CPU/memory stressor.
    """

    return get_custom_object(
        "chaos-mesh.org",
        "v1alpha1",
        "stresschaos",
        name,
        ns,
        secrets=secrets,
    )
