# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from chaoslib.exceptions import FailedActivity
from kubernetes import client, config
import pytest

from chaosk8s.probes import all_microservices_healthy, \
    microservice_available_and_healthy, microservice_is_not_available, \
    service_endpoint_is_initialized


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
    deployment = MagicMock()
    result = MagicMock()
    result.items = [deployment]

    v1 = MagicMock()
    v1.list_namespaced_deployment.return_value = result
    client.AppsV1beta1Api.return_value = v1

    with pytest.raises(FailedActivity) as excinfo:
        microservice_is_not_available("mysvc")
    assert "microservice 'mysvc' looks healthy" in str(excinfo)


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
