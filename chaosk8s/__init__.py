# -*- coding: utf-8 -*-
import os
import os.path

from kubernetes import client, config

__all__ = ["create_k8s_api_client", "__version__"]
__version__ = '0.3.0'


def create_k8s_api_client() -> client.ApiClient:
    """
    Create a Kubernetes client from either the local config or, if none is
    found, from the following variables:

    * KUBERNETES_HOST: Kubernetes API address

    You can authenticate with a token via:
    * KUBERNETES_API_KEY: the API key to authenticate with
    * KUBERNETES_API_KEY_PREFIX: the key kind, if not set, defaults to "Bearer"

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
    """
    env = os.environ

    config_path = os.path.expanduser(env.get('KUBECONFIG', '~/.kube/config'))

    if os.path.exists(config_path):
        return config.new_client_from_config()

    configuration = client.Configuration()
    configuration.host = env.get("KUBERNETES_HOST", "http://localhost")
    configuration.verify_ssl = "KUBERNETES_VERIFY_SSL" in env
    configuration.cert_file = env.get("KUBERNETES_CA_CERT_FILE")

    if "KUBERNETES_API_KEY" in env:
        configuration.api_key['authorization'] = env.get("KUBERNETES_API_KEY")
        configuration.api_key_prefix['authorization'] = env.get(
            "KUBERNETES_API_KEY_PREFIX", "Bearer")
    elif "KUBERNETES_CERT_FILE" in env:
        configuration.cert_file = env["KUBERNETES_CERT_FILE"]
        configuration.key_file = env["KUBERNETES_KEY_FILE"]
    elif "KUBERNETES_USERNAME" in env:
        configuration.username = env["KUBERNETES_USERNAME"]
        configuration.password = env.get("KUBERNETES_PASSWORD", "")

    return client.ApiClient(configuration)
