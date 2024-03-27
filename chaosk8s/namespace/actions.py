import json
import os.path

import yaml
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = ["create_namespace", "delete_namespace"]


def create_namespace(
    name: str = None, spec_path: str = None, secrets: Secrets = None
):
    """
    Create a namespace from the specified spec_path, which must be
    the path to the JSON or YAML representation of the namespace.
    """
    api = create_k8s_api_client(secrets)

    if spec_path:
        with open(spec_path) as f:
            p, ext = os.path.splitext(spec_path)
            if ext == ".json":
                ns = json.loads(f.read())
            elif ext in [".yml", ".yaml"]:
                ns = yaml.safe_load(f.read())
            else:
                raise ActivityFailed(f"cannot process {spec_path}")

    elif name:
        ns = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": name},
        }
    else:
        raise ActivityFailed("You need to either specify name or spec_path")
    v1 = client.CoreV1Api(api)
    v1.create_namespace(body=ns)


def delete_namespace(name: str, secrets: Secrets = None):
    """
    Remove the given namespace
    """
    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    v1.delete_namespace(name)
