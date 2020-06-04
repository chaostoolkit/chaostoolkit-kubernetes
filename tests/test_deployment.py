# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock, ANY, call

import pytest
import urllib3
from chaoslib.exceptions import ActivityFailed
from kubernetes.client.models import V1DeploymentList, V1Deployment, V1ObjectMeta

from chaosk8s.deployment.actions import create_deployment, delete_deployment, \
    scale_deployment, update_image
from chaosk8s.deployment.probes import deployment_not_fully_available, \
    deployment_available_and_healthy, deployment_fully_available


@patch('chaosk8s.has_local_config_file', autospec=True)
def test_cannot_process_other_than_yaml_and_json(has_conf):
    has_conf.return_value = False
    path = "./tests/fixtures/invalid-k8s.txt"
    with pytest.raises(ActivityFailed) as excinfo:
        create_deployment(spec_path=path)
    assert "cannot process {path}".format(path=path) in str(excinfo)


@patch('builtins.open', autospec=True)
@patch('chaosk8s.deployment.actions.json', autospec=True)
@patch('chaosk8s.deployment.actions.create_k8s_api_client', autospec=True)
@patch('chaosk8s.deployment.actions.client', autospec=True)
def test_create_deployment(client, api, json, open):
    v1 = MagicMock()
    client.AppsV1beta1Api.return_value = v1
    json.loads.return_value = {"Kind": "Deployment"}

    create_deployment(spec_path="depl.json")

    v1.create_namespaced_deployment.assert_called_with(ANY, body=json.loads.return_value)


@patch('chaosk8s.deployment.actions.create_k8s_api_client', autospec=True)
@patch('chaosk8s.deployment.actions.client', autospec=True)
def test_update_image_when_container_is_found(client, api):
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1
    deployment_mock = MagicMock()
    container_mock = MagicMock()
    container_mock.name = "container_name"
    deployment_mock.spec.template.spec.containers = [container_mock]
    v1.read_namespaced_deployment.return_value = deployment_mock
    update_image(name="deployment_name",
                 image="image:tag",
                 ns="default",
                 container_name=container_mock.name)
    v1.replace_namespaced_deployment.assert_called_once()


@patch('chaosk8s.deployment.actions.create_k8s_api_client', autospec=True)
@patch('chaosk8s.deployment.actions.client', autospec=True)
def test_update_image_when_container_is_not_found(client, api):
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1
    deployment_mock = MagicMock()
    container_mock = MagicMock()
    container_mock.name = "container_name"
    deployment_mock.spec.template.spec.containers = [container_mock]
    v1.read_namespaced_deployment.return_value = deployment_mock
    with pytest.raises(ActivityFailed) as excinfo:
        update_image(name="deployment_name",
                 image="image:tag",
                 ns="default",
                 container_name="not_container_name")
    assert "container with the given name was not found" in str(excinfo)


@patch('chaosk8s.deployment.actions.create_k8s_api_client', autospec=True)
@patch('chaosk8s.deployment.actions.client', autospec=True)
def test_delete_deployment(client, api):
    depl1 = V1Deployment(metadata=V1ObjectMeta(name="depl1"))
    depl2 = V1Deployment(metadata=V1ObjectMeta(name="depl2"))
    v1 = MagicMock()
    client.AppsV1beta1Api.return_value = v1
    v1.list_namespaced_deployment.return_value = V1DeploymentList(items=(depl1, depl2))

    delete_deployment("fake_name", "fake_ns")

    v1.list_namespaced_deployment.assert_called_with("fake_ns", label_selector=ANY)
    v1.delete_namespaced_deployment.assert_has_calls(
        calls=[
            call(depl1.metadata.name, "fake_ns", body=ANY),
            call(depl2.metadata.name, "fake_ns", body=ANY)
        ],
        any_order=True
    )


@patch('chaosk8s.deployment.actions.create_k8s_api_client', autospec=True)
@patch('chaosk8s.deployment.actions.client', autospec=True)
def test_scale_deployment(client, api):
    v1 = MagicMock()
    client.ExtensionsV1beta1Api.return_value = v1

    scale_deployment("fake", 3, "fake_ns")

    body = {"spec": {"replicas": 3}}
    v1.patch_namespaced_deployment_scale.assert_called_with("fake", namespace="fake_ns", body=body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.deployment.probes.watch', autospec=True)
@patch('chaosk8s.deployment.probes.client', autospec=True)
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

    with pytest.raises(ActivityFailed) as excinfo:
        deployment_not_fully_available("mysvc")
    assert "deployment 'mysvc' failed to stop running within" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.deployment.probes.client', autospec=True)
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

    with pytest.raises(ActivityFailed) as excinfo:
        deployment_available_and_healthy("mysvc")
    assert "Deployment 'mysvc' was not found" in str(excinfo)

    deployment = MagicMock()
    deployment.spec.replicas = 2
    deployment.status.available_replicas = 1
    result.items.append(deployment)

    with pytest.raises(ActivityFailed) as excinfo:
        deployment_available_and_healthy("mysvc")
    assert "Deployment 'mysvc' is not healthy" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.deployment.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_expecting_a_healthy_microservice(cl,
                                          client,
                                          has_conf):
    has_conf.return_value = False
    result = MagicMock()
    result.items = []

    v1 = MagicMock()
    v1.list_namespaced_deployment.return_value = result
    client.AppsV1beta1Api.return_value = v1

    deployment = MagicMock()
    deployment.spec.replicas = 2
    deployment.status.available_replicas = 2
    result.items.append(deployment)

    assert deployment_available_and_healthy("mysvc") is True


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.deployment.probes.watch', autospec=True)
@patch('chaosk8s.deployment.probes.client', autospec=True)
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

    with pytest.raises(ActivityFailed) as excinfo:
        deployment_not_fully_available("mysvc")
    assert "deployment 'mysvc' failed to stop running within" in str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.deployment.probes.watch', autospec=True)
@patch('chaosk8s.deployment.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_deployment_is_fully_available(cl, client, watch, has_conf):
    has_conf.return_value = False
    deployment = MagicMock()
    deployment.spec.replicas = 2
    deployment.status.ready_replicas = 2

    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = [[{"object": deployment, "type": "ADDED"}]]
    watch.Watch.return_value = watcher

    assert deployment_fully_available("mysvc") is True


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.deployment.probes.watch', autospec=True)
@patch('chaosk8s.deployment.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_deployment_is_not_fully_available_when_it_should(cl, client,
                                                          watch, has_conf):
    has_conf.return_value = False
    deployment = MagicMock()
    deployment.spec.replicas = 2
    deployment.status.ready_replicas = 1

    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = urllib3.exceptions.ReadTimeoutError(
        None, None, None)
    watch.Watch.return_value = watcher

    with pytest.raises(ActivityFailed) as excinfo:
        deployment_fully_available("mysvc")
    assert "deployment 'mysvc' failed to recover within" in str(excinfo)
