from textwrap import dedent
from typing import Any, Dict, List, Optional, Union

import yaml
from chaoslib.types import Secrets

from chaosk8s.crd.actions import create_custom_object, delete_custom_object

__all__ = [
    "stress_memory",
    "stress_cpu",
    "delete_stressor",
]


def stress_cpu(
    name: str,
    workers: int,
    load: int,
    ns: str = "default",
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    duration: str = "30s",
    container_names: Optional[Union[str, List[str]]] = None,
    stressng_stressors: Optional[str] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Stress the CPU to impact a process/container.

    See: https://chaos-mesh.org/docs/simulate-heavy-stress-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: StressChaos
    metadata: {}
    spec:
      selector: {}
      stressors:
        cpu: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    c = s["stressors"]["cpu"]
    c["workers"] = workers
    c["load"] = load

    s["mode"] = mode
    if mode == "fixed-percent":
        s["value"] = mode_value

    s["duration"] = duration
    s["direction"] = direction

    if isinstance(container_names, str):
        container_names = container_names.split(",")

    s["containerNames"] = container_names

    if stressng_stressors:
        s["stressngStressors"] = stressng_stressors

    add_common_spec(
        r,
        namespaces_selectors,
        label_selectors,
        annotations_selectors,
        mode,
        mode_value,
        direction,
    )

    return create_custom_object(
        "chaos-mesh.org",
        "v1alpha1",
        "stresschaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def stress_memory(
    name: str,
    workers: Optional[int] = None,
    size: Optional[str] = None,
    oom_score: Optional[int] = None,
    time_to_get_to_size: Optional[str] = None,
    ns: str = "default",
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    duration: str = "30s",
    container_names: Optional[Union[str, List[str]]] = None,
    stressng_stressors: Optional[str] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Stress the memory to impact a process/container.

    See: https://chaos-mesh.org/docs/simulate-heavy-stress-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: StressChaos
    metadata: {}
    spec:
      selector: {}
      stressors:
        memory: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    c = s["stressors"]["memory"]
    c["workers"] = workers
    c["size"] = size
    c["time"] = time_to_get_to_size
    c["oomScoreAdj"] = oom_score

    s["mode"] = mode
    if mode == "fixed-percent":
        s["value"] = mode_value

    s["duration"] = duration
    s["direction"] = direction

    if isinstance(container_names, str):
        container_names = container_names.split(",")

    s["containerNames"] = container_names

    if stressng_stressors:
        s["stressngStressors"] = stressng_stressors

    add_common_spec(
        r,
        namespaces_selectors,
        label_selectors,
        annotations_selectors,
        mode,
        mode_value,
        direction,
    )

    return create_custom_object(
        "chaos-mesh.org",
        "v1alpha1",
        "stresschaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def delete_stressor(
    name: str,
    ns: str = "default",
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Remove a Chaos Mesh stressor.
    """

    return delete_custom_object(
        "chaos-mesh.org",
        "v1alpha1",
        "stresschaos",
        name,
        ns,
        secrets=secrets,
    )


###############################################################################
# Private functions
###############################################################################
def add_common_spec(
    resource: Dict[str, Any],
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
) -> None:
    s = resource["spec"]

    s["direction"] = direction

    s["mode"] = mode
    if mode == "fixed-percent":
        s["value"] = mode_value

    s["direction"] = direction

    if namespaces_selectors:
        if isinstance(namespaces_selectors, str):
            namespaces_selectors = namespaces_selectors.split(",")

        s["selector"]["namespaces"] = namespaces_selectors

    if label_selectors:
        selectors = label_selectors
        if isinstance(label_selectors, str):
            selectors = {}
            for ls in label_selectors.split(","):
                k, v = ls.split("=", 1)
                selectors[k] = v
        s["selector"]["labelSelectors"] = selectors

    if annotations_selectors:
        selectors = annotations_selectors
        if isinstance(annotations_selectors, str):
            selectors = {}
            for ls in annotations_selectors.split(","):
                k, v = ls.split("=", 1)
                selectors[k] = v
        s["selector"]["annotationSelectors"] = selectors
