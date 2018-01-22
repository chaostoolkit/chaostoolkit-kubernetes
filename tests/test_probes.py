# -*- coding: utf-8 -*-
import io
from unittest.mock import MagicMock, patch
import urllib3

from chaoslib.exceptions import FailedActivity
from kubernetes import client, config
import pytest

from chaosk8s.probes import all_microservices_healthy, \
    microservice_available_and_healthy, microservice_is_not_available, \
    service_endpoint_is_initialized, deployment_is_not_fully_available, \
    read_microservices_logs


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_unhealthy_system_should_be_reported(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status.phase = "Failed"

    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    with pytest.raises(FailedActivity) as excinfo:
        all_microservices_healthy()
    assert "the system is unhealthy" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_expecting_a_healthy_microservice_should_be_reported_when_not(cl,
                                                                      client,
                                                                      has_conf):
    has_conf.return_value = False
    result = MagicMock()
    result.items = []

    v1 = MagicMock()
    v1.list_namespaced_deployment.return_value = result
    client.AppsV1beta1Api.return_value = v1

    with pytest.raises(FailedActivity) as excinfo:
        microservice_available_and_healthy("mysvc")
    assert "microservice 'mysvc' was not found" in str(excinfo)

    deployment = MagicMock()
    deployment.spec.replicas = 2
    deployment.status.available_replicas = 1
    result.items.append(deployment)

    with pytest.raises(FailedActivity) as excinfo:
        microservice_available_and_healthy("mysvc")
    assert "microservice 'mysvc' is not healthy" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_expecting_microservice_is_there_when_it_should_not(cl, client, 
                                                            has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status.phase = "Running"
    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    with pytest.raises(FailedActivity) as excinfo:
        microservice_is_not_available("mysvc")
    assert "microservice 'mysvc' is actually running" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_expecting_service_endpoint_should_be_initialized(cl, client,
                                                          has_conf):
    has_conf.return_value = False
    service = MagicMock()
    result = MagicMock()
    result.items = [service]

    v1 = MagicMock()
    v1.list_namespaced_service.return_value = result
    client.CoreV1Api.return_value = v1

    assert service_endpoint_is_initialized("mysvc") is True


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_unitialized_or_not_existing_service_endpoint_should_not_be_considered_available(
    cl, client, has_conf):
    has_conf.return_value = False
    service = MagicMock()
    result = MagicMock()
    result.items = []

    v1 = MagicMock()
    v1.list_namespaced_service.return_value = result
    client.CoreV1Api.return_value = v1

    with pytest.raises(FailedActivity) as excinfo:
        service_endpoint_is_initialized("mysvc")
    assert "service 'mysvc' is not initialized" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.watch', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_deployment_is_not_fully_available(cl, client, watch, has_conf):
    has_conf.return_value = False
    deployment = MagicMock()
    deployment.spec.replicas = 2
    deployment.status.ready_replicas = 1

    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = [[{"object": deployment, "type": "ADDED"}]]
    watch.Watch.return_value = watcher

    assert deployment_is_not_fully_available("mysvc") is True


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.watch', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_deployment_is_fully_available_when_it_should_not(cl, client,
                                                          watch, has_conf):
    has_conf.return_value = False
    deployment = MagicMock()
    deployment.spec.replicas = 2
    deployment.status.ready_replicas = 2

    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = urllib3.exceptions.ReadTimeoutError(
        None, None, None)
    watch.Watch.return_value = watcher

    with pytest.raises(FailedActivity) as excinfo:
        deployment_is_not_fully_available("mysvc")
    assert "microservice 'mysvc' failed to stop running within" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_fetch_last_logs(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.metadata.name = "myapp-1235"
    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    v1.read_namespaced_pod_log.return_value = io.BytesIO(b"hello")

    logs = read_microservices_logs("myapp")

    assert pod.metadata.name in logs
    assert logs[pod.metadata.name] == "hello"


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_can_select_by_label(cl, client, has_conf):
    has_conf.return_value = False
    result = MagicMock()
    result.items = [MagicMock()]

    v1 = MagicMock()
    v1.list_namespaced_service.return_value = result
    client.CoreV1Api.return_value = v1

    label_selector = "app=my-super-app"
    service_endpoint_is_initialized("mysvc", label_selector=label_selector)
    v1.list_namespaced_service.assert_called_with(
        "default", label_selector=label_selector
    )
