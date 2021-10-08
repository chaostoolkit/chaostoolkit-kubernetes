# -*- coding: utf-8 -*-
import json
import os.path

import yaml
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Secrets
from kubernetes import client

from chaosk8s import create_k8s_api_client

__all__ = ["create_service_endpoint", "delete_service"]


def create_service_endpoint(
    spec_path: str, ns: str = "default", secrets: Secrets = None
):
    """
    Create a service endpoint described by the service config, which must be
    the path to the JSON or YAML representation of the service.
    """
    api = create_k8s_api_client(secrets)

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == ".json":
            service = json.loads(f.read())
        elif ext in [".yml", ".yaml"]:
            service = yaml.safe_load(f.read())
        else:
            raise ActivityFailed("cannot process {path}".format(path=spec_path))

    v1 = client.CoreV1Api(api)
    v1.create_namespaced_service(ns, body=service)


def delete_service(name: str, ns: str = "default", secrets: Secrets = None):
    """
    Remove the given service
    """
    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    v1.delete_namespaced_service(name, namespace=ns)
