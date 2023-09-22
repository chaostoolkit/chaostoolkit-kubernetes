import os
import os.path
from typing import List

from chaoslib.discovery.discover import (
    discover_actions,
    discover_probes,
    initialize_discovery_result,
)
from chaoslib.types import DiscoveredActivities, Discovery, Secrets
from kubernetes import client, config
from logzero import logger

__all__ = ["create_k8s_api_client", "discover", "__version__"]
__version__ = "0.30.0"


def get_config_path() -> str:
    return os.path.expanduser(os.environ.get("KUBECONFIG", "~/.kube/config"))


def has_local_config_file(config_file: str = None):
    config_path = config_file or get_config_path()
    return os.path.exists(config_path)


def create_k8s_api_client(secrets: Secrets = None) -> client.ApiClient:
    """
    Create a Kubernetes client from:

    1. From a local configuration file if it exists (`~/.kube/config`). You
       can specify which context you want to use as well through the
       `KUBERNETES_CONTEXT` key in the environment or in the `secrets` object.
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

    verify_ssl = lookup("KUBERNETES_VERIFY_SSL", False) is not False
    debug = lookup("KUBERNETES_DEBUG", False) is not False
    config_file = get_config_path()

    if has_local_config_file(config_file):
        context = lookup("KUBERNETES_CONTEXT")
        logger.debug(
            f"Using Kubernetes context '{context or 'default'}' "
            f"from config '{config_file}'"
        )

        config.load_kube_config(context=context)
        client.Configuration.verify_ssl = verify_ssl
        client.Configuration.debug = debug

        proxy_url = os.getenv("HTTP_PROXY", None)
        if proxy_url:
            client.Configuration._default.proxy = proxy_url
        no_proxy = os.getenv("NO_PROXY", None)
        if no_proxy:
            client.Configuration._default.no_proxy = no_proxy

        return client.ApiClient()

    elif env.get("CHAOSTOOLKIT_IN_POD") == "true":
        config.load_incluster_config()
        client.Configuration.verify_ssl = verify_ssl
        client.Configuration.debug = debug

        proxy_url = os.getenv("HTTP_PROXY", None)
        if proxy_url:
            client.Configuration._default.proxy = proxy_url
        no_proxy = os.getenv("NO_PROXY", None)
        if no_proxy:
            client.Configuration._default.no_proxy = no_proxy

        return client.ApiClient()

    else:
        configuration = client.Configuration()
        configuration.debug = debug
        configuration.host = lookup("KUBERNETES_HOST", "http://localhost")
        configuration.verify_ssl = lookup("KUBERNETES_VERIFY_SSL", False) is not False
        configuration.ssl_ca_cert = lookup("KUBERNETES_CA_CERT_FILE")

        if "KUBERNETES_API_KEY" in env or "KUBERNETES_API_KEY" in secrets:
            configuration.api_key["authorization"] = lookup("KUBERNETES_API_KEY")
            configuration.api_key_prefix["authorization"] = lookup(
                "KUBERNETES_API_KEY_PREFIX", "Bearer"
            )
        elif "KUBERNETES_CERT_FILE" in env or "KUBERNETES_CERT_FILE" in secrets:
            configuration.cert_file = lookup("KUBERNETES_CERT_FILE")
            configuration.key_file = lookup("KUBERNETES_KEY_FILE")
        elif "KUBERNETES_USERNAME" in env or "KUBERNETES_USERNAME" in secrets:
            configuration.username = lookup("KUBERNETES_USERNAME")
            configuration.password = lookup("KUBERNETES_PASSWORD", "")

        proxy_url = os.getenv("HTTP_PROXY", None)
        if proxy_url:
            configuration.proxy = proxy_url
        no_proxy = os.getenv("NO_PROXY", None)
        if no_proxy:
            configuration.no_proxy = no_proxy

    return client.ApiClient(configuration)


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover Kubernetes capabilities offered by this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-kubernetes")

    discovery = initialize_discovery_result(
        "chaostoolkit-kubernetes", __version__, "kubernetes"
    )
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
    activities.extend(discover_actions("chaosk8s.daemonset.actions"))
    activities.extend(discover_actions("chaosk8s.daemonset.probes"))
    activities.extend(discover_actions("chaosk8s.deployment.actions"))
    activities.extend(discover_actions("chaosk8s.deployment.probes"))
    activities.extend(discover_actions("chaosk8s.namespace.actions"))
    activities.extend(discover_actions("chaosk8s.namespace.probes"))
    activities.extend(discover_actions("chaosk8s.networking.actions"))
    activities.extend(discover_actions("chaosk8s.networking.probes"))
    activities.extend(discover_actions("chaosk8s.node.actions"))
    activities.extend(discover_actions("chaosk8s.node.probes"))
    activities.extend(discover_actions("chaosk8s.pod.actions"))
    activities.extend(discover_probes("chaosk8s.pod.probes"))
    activities.extend(discover_actions("chaosk8s.replicaset.actions"))
    activities.extend(discover_actions("chaosk8s.service.actions"))
    activities.extend(discover_actions("chaosk8s.service.probes"))
    activities.extend(discover_actions("chaosk8s.secret.actions"))
    activities.extend(discover_actions("chaosk8s.secret.probes"))
    activities.extend(discover_actions("chaosk8s.statefulset.actions"))
    activities.extend(discover_probes("chaosk8s.statefulset.probes"))
    activities.extend(discover_actions("chaosk8s.crd.actions"))
    activities.extend(discover_probes("chaosk8s.crd.probes"))
    activities.extend(discover_actions("chaosk8s.chaosmesh.network.actions"))
    activities.extend(discover_actions("chaosk8s.chaosmesh.stress.actions"))
    activities.extend(discover_probes("chaosk8s.chaosmesh.network.probes"))
    activities.extend(discover_probes("chaosk8s.chaosmesh.stress.probes"))
    return activities


def _log_deprecated(name: str, alt_name: str):
    logger.warning(
        f"{name} function is DEPRECATED and will be removed in the next \
        releases, please use {alt_name} instead"
    )
