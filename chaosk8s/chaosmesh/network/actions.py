from textwrap import dedent
from typing import Any, Dict, List, Optional, Union

import yaml
from chaoslib.types import Secrets

from chaosk8s.crd.actions import create_custom_object, delete_custom_object

__all__ = [
    "add_latency",
    "set_loss",
    "duplicate_packets",
    "corrupt_packets",
    "reorder_packets",
    "set_bandwidth",
    "delete_network_fault",
]


def add_latency(
    name: str,
    ns: str = "default",
    namespaces_selectors: Optional[Union[str, List[str]]] = None,
    label_selectors: Optional[Union[str, Dict[str, Any]]] = None,
    annotations_selectors: Optional[Union[str, Dict[str, Any]]] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    latency: Optional[str] = None,
    correlation: Optional[str] = None,
    jitter: Optional[str] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Set network delay on a pod.

    See: https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: NetworkChaos
    metadata: {}
    spec:
      action: delay
      selector: {}
      delay: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    d = s["delay"]

    if latency:
        d["latency"] = latency

    if correlation:
        d["correlation"] = correlation

    if jitter:
        d["jitter"] = jitter

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
        "networkchaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def set_loss(
    name: str,
    ns: str = "default",
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    loss: Optional[str] = None,
    correlation: Optional[str] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Set network loss on a pod.

    See: https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: NetworkChaos
    metadata: {}
    spec:
      action: loss
      selector: {}
      loss: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    d = s["loss"]

    if loss:
        d["loss"] = loss

    if correlation:
        d["correlation"] = correlation

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
        "networkchaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def duplicate_packets(
    name: str,
    ns: str = "default",
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    duplicate: Optional[str] = None,
    correlation: Optional[str] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Duplicate network packets on a pod.

    See: https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: NetworkChaos
    metadata: {}
    spec:
      action: duplicate
      selector: {}
      duplicate: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    d = s["duplicate"]

    if duplicate:
        d["duplicate"] = duplicate

    if correlation:
        d["correlation"] = correlation

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
        "networkchaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def reorder_packets(
    name: str,
    ns: str = "default",
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    reorder: Optional[str] = None,
    correlation: Optional[str] = None,
    gap: Optional[str] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Reorder network packets on a pod.

    See: https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: NetworkChaos
    metadata: {}
    spec:
      action: reorder
      selector: {}
      reorder: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    d = s["reorder"]

    if reorder:
        d["reorder"] = reorder

    if gap:
        d["gap"] = gap

    if correlation:
        d["correlation"] = correlation

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
        "networkchaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def corrupt_packets(
    name: str,
    ns: str = "default",
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    corrupt: Optional[str] = None,
    correlation: Optional[str] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Corrupt network packets on a pod.

    See: https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: NetworkChaos
    metadata: {}
    spec:
      action: corrupt
      selector: {}
      corrupt: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    d = s["corrupt"]

    if corrupt:
        d["corrupt"] = corrupt

    if correlation:
        d["correlation"] = correlation

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
        "networkchaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def set_bandwidth(
    name: str,
    rate: str,
    limit: int,
    buffer: int,
    ns: str = "default",
    namespaces_selectors: Optional[str] = None,
    label_selectors: Optional[str] = None,
    annotations_selectors: Optional[str] = None,
    mode: str = "one",
    mode_value: Optional[str] = None,
    direction: str = "to",
    peakrate: Optional[int] = None,
    minburst: Optional[int] = None,
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Simulate bandwdith on a pod.

    See: https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/
    """

    r = yaml.safe_load(
        dedent(
            """---
    apiVersion: chaos-mesh.org/v1alpha1
    kind: NetworkChaos
    metadata: {}
    spec:
      action: bandwdith
      selector: {}
      bandwidth: {}
    """
        )
    )

    r["metadata"]["name"] = name
    r["metadata"]["ns"] = ns

    s = r["spec"]
    d = s["bandwidth"]

    d["rate"] = rate
    d["limit"] = limit
    d["buffer"] = buffer

    if peakrate:
        d["peakrate"] = peakrate

    if minburst:
        d["minburst"] = minburst

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
        "networkchaos",
        ns,
        resource=r,
        secrets=secrets,
    )


def delete_network_fault(
    name: str,
    ns: str = "default",
    secrets: Secrets = None,
) -> Dict[str, Any]:
    """
    Remove a Chaos Mesh network fault.
    """

    return delete_custom_object(
        "chaos-mesh.org",
        "v1alpha1",
        "networkchaos",
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
