# -*- coding: utf-8 -*-
import json
import os
import os.path
from typing import List

from chaoslib.discovery.discover import discover_actions, discover_probes, \
    initialize_discovery_result
from chaoslib.exceptions import DiscoveryFailed
from chaoslib.types import Discovery, DiscoveredActivities, \
    DiscoveredSystemInfo, Secrets
from kubernetes import client, config
from logzero import logger


__all__ = ["create_k8s_api_client", "discover", "__version__"]
__version__ = '0.15.0'


def has_local_config_file():
    config_path = os.path.expanduser(
        os.environ.get('KUBECONFIG', '~/.kube/config'))
    return os.path.exists(config_path)


def create_k8s_api_client(secrets: Secrets = None) -> client.ApiClient:
    """
    Create a Kubernetes client from:

    1. From a local configuration file if it exists (`~/.kube/config`)
    2. From the cluster configuration if executed from a Kubernetes pod and
       the CHAOSTOOLKIT_IN_POD is set to `"true"`.
    3. From a mix of the following environment keys:

        * KUBERNETES_HOST: Kubernetes API address

        You can authenticate with a token via:
        * KUBERNETES_API_KEY: the API key to authenticate with
        * KUBERNETES_API_KEY_PREFIX: the key kind, if not set, defaults to
          "Bearer"

        Or via a username/password:
        * KUBERNETES_USERNAME
        * KUBERNETES_PASSWORD

        Or via SSL:
        * KUBERNETES_CERT_FILE
        * KUBERNETES_KEY_FILE

        Finally, you may disable SSL verification against HTTPS endpoints:
        * KUBERNETES_VERIFY_SSL: should we verify the SSL (unset means no)
        * KUBERNETES_CA_CERT_FILE: path the CA certificate when verification is
          expected

        You may pass a secrets dictionary, in which case, values will be looked
        there before the environ.
    """
    env = os.environ
    secrets = secrets or {}

    def lookup(k: str, d: str = None) -> str:
        return secrets.get(k, env.get(k, d))

    if has_local_config_file():
        return config.new_client_from_config()

    elif env.get("CHAOSTOOLKIT_IN_POD") == "true":
        config.load_incluster_config()
        return client.ApiClient()

    else:
        configuration = client.Configuration()
        configuration.debug = True
        configuration.host = lookup("KUBERNETES_HOST", "http://localhost")
        configuration.verify_ssl = lookup(
            "KUBERNETES_VERIFY_SSL", False) is not False
        configuration.cert_file = lookup("KUBERNETES_CA_CERT_FILE")

        if "KUBERNETES_API_KEY" in env or "KUBERNETES_API_KEY" in secrets:
            configuration.api_key['authorization'] = lookup(
                "KUBERNETES_API_KEY")
            configuration.api_key_prefix['authorization'] = lookup(
                "KUBERNETES_API_KEY_PREFIX", "Bearer")
        elif "KUBERNETES_CERT_FILE" in env or \
                "KUBERNETES_CERT_FILE" in secrets:
            configuration.cert_file = lookup("KUBERNETES_CERT_FILE")
            configuration.key_file = lookup("KUBERNETES_KEY_FILE")
        elif "KUBERNETES_USERNAME" in env or "KUBERNETES_USERNAME" in secrets:
            configuration.username = lookup("KUBERNETES_USERNAME")
            configuration.password = lookup("KUBERNETES_PASSWORD", "")

    return client.ApiClient(configuration)


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover Kubernetes capabilities offered by this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-kubernetes")

    discovery = initialize_discovery_result(
        "chaostoolkit-kubernetes", __version__, "kubernetes")
    discovery["activities"].extend(load_exported_activities())
    return discovery


###############################################################################
# Private functions
###############################################################################
def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions and probes exposed by this extension.
    """
    activities = []
    activities.extend(discover_actions("chaosk8s.actions"))
    activities.extend(discover_probes("chaosk8s.probes"))
    activities.extend(discover_actions("chaosk8s.pod.actions"))
    activities.extend(discover_probes("chaosk8s.pod.probes"))
    activities.extend(discover_actions("chaosk8s.node.actions"))
    return activities
