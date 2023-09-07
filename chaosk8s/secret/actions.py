import json
import os.path

import yaml
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = ["create_secret", "delete_secret"]


def create_secret(spec_path: str, ns: str = "default", secrets: Secrets = None):
    """
    Create a secret endpoint described by the secret config, which must be
    the path to the JSON or YAML representation of the secret.
    """
    api = create_k8s_api_client(secrets)

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == ".json":
            secret = json.loads(f.read())
        elif ext in [".yml", ".yaml"]:
            secret = yaml.safe_load(f.read())
        else:
            raise ActivityFailed(f"cannot process {spec_path}")

    v1 = client.CoreV1Api(api)
    v1.create_namespaced_secret(ns, body=secret)


def delete_secret(name: str, ns: str = "default", secrets: Secrets = None):
    """
    Remove the given secret
    """
    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    v1.delete_namespaced_secret(name, namespace=ns)
