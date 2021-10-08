import json
import os.path
from typing import Any, Dict

import yaml
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = [
    "create_network_policy",
    "remove_network_policy",
    "deny_all_ingress",
    "remove_deny_all_ingress",
    "deny_all_egress",
    "remove_deny_all_egress",
    "allow_dns_access",
    "remove_allow_dns_access",
]


def create_network_policy(
    spec: Dict[str, Any] = None,
    spec_path: str = None,
    ns: str = "default",
    secrets: Secrets = None,
):
    """
    Create a network policy in the given namespace eitehr from the definition
    as `spec` or from a file containing the definition at `spec_path`.
    """
    api = create_k8s_api_client(secrets)

    if spec_path and os.path.isfile(spec_path):
        with open(spec_path) as f:
            p, ext = os.path.splitext(spec_path)
            if ext == ".json":
                spec = json.loads(f.read())
            elif ext in [".yml", ".yaml"]:
                spec = yaml.safe_load(f.read())
            else:
                raise ActivityFailed(f"cannot process {spec_path}")

    v1 = client.NetworkingV1Api(api)
    v1.create_namespaced_network_policy(ns, body=spec)


def remove_network_policy(name: str, ns: str = "default", secrets: Secrets = None):
    """
    Create a network policy in the given namespace eitehr from the definition
    as `spec` or from a file containing the definition at `spec_path`.
    """
    api = create_k8s_api_client(secrets)
    v1 = client.NetworkingV1Api(api)
    v1.delete_namespaced_network_policy(name, ns)


def deny_all_ingress(
    label_selectors: Dict[str, Any] = None, ns: str = "default", secrets: Secrets = None
):
    """
    Convenient helper policy to deny ingress network to all pods in a
    namespace, unless `label_selectors, in which case, only matching pods will
    be impacted.
    """
    pod_selector = {}
    if label_selectors:
        pod_selector["matchLabels"] = label_selectors

    create_network_policy(
        spec={
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "chaostoolkit-deny-all-ingress"},
            "spec": {
                "podSelector": pod_selector,
                "policyTypes": ["Ingress"],
                "ingress": [],
            },
        },
        ns=ns,
        secrets=secrets,
    )


def remove_deny_all_ingress(ns: str = "default", secrets: Secrets = None):
    """
    Remove the rule set by the `deny_all_ingress` action.
    """
    remove_network_policy("chaostoolkit-deny-all-ingress", ns=ns, secrets=secrets)


def deny_all_egress(
    label_selectors: Dict[str, Any] = None, ns: str = "default", secrets: Secrets = None
):
    """
    Convenient helper rule to deny all egress network from all pods in a
    namespace, unless `label_selectors, in which case, only matching pods will
    be impacted.
    """
    pod_selector = {}
    if label_selectors:
        pod_selector["matchLabels"] = label_selectors

    create_network_policy(
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "chaostoolkit-deny-all-egress"},
            "spec": {"podSelector": pod_selector, "policyTypes": ["Egress"]},
        },
        ns=ns,
        secrets=secrets,
    )


def remove_deny_all_egress(ns: str = "default", secrets: Secrets = None):
    """
    Remove the rule set by the `deny_all_egress` action.
    """
    remove_network_policy("chaostoolkit-deny-all-egress", ns=ns, secrets=secrets)


def allow_dns_access(
    label_selectors: Dict[str, Any] = None, ns: str = "default", secrets: Secrets = None
):
    """
    Convenient helper rule to DNS access from all pods
    in a namespace, unless `label_selectors, in which case, only matching pods
    will be impacted.
    """
    pod_selector = {}
    if label_selectors:
        pod_selector["matchLabels"] = label_selectors

    create_network_policy(
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "chaostoolkit-allow-dns"},
            "spec": {
                "podSelector": pod_selector,
                "policyTypes": ["Egress"],
                "egress": [
                    {
                        "to": [{"namespaceSelector": {}}],
                        "ports": [
                            {"port": 53, "protocol": "UDP"},
                            {"port": 53, "protocol": "TCP"},
                        ],
                    }
                ],
            },
        },
        ns=ns,
        secrets=secrets,
    )


def remove_allow_dns_access(ns: str = "default", secrets: Secrets = None):
    """
    Remove the rule set by the `allow_dns_access` action.
    """
    remove_network_policy("chaostoolkit-allow-dns", ns=ns, secrets=secrets)
