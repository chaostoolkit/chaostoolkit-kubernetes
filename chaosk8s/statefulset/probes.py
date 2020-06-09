import datetime
import time

from logzero import logger

from chaosk8s import create_k8s_api_client
from chaoslib import Secrets, ActivityFailed
from kubernetes import client

__all__ = ["wait_to_be_healthy"]


def wait_to_be_healthy(
        name: str, timeout_secs: int, interval_secs: int, ns: str = "default",
        secrets: Secrets = None):
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1Api(api)
    current_time = datetime.datetime.now()
    timeout = current_time + datetime.timedelta(0, timeout_secs)
    while datetime.datetime.now() < timeout:
        statefulset = v1.read_namespaced_stateful_set(name, ns)
        desired_replicas = statefulset.spec.replicas
        ready_replicas = statefulset.status.ready_replicas
        logger.info(
            "probe found {} ready replicas compared to {} expected replicas".
            format(ready_replicas, desired_replicas)
        )
        if desired_replicas == ready_replicas:
            return
        time.sleep(interval_secs)
    raise ActivityFailed(
        "statefulset {} failed to reach a healthy state after {} seconds".
        format(name, timeout_secs)
    )
