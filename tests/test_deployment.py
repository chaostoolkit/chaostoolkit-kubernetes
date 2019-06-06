# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock, ANY, call

import pytest
from chaoslib.exceptions import ActivityFailed
from kubernetes.client.models import V1DeploymentList, V1Deployment, V1ObjectMeta

from chaosk8s.deployment.actions import create_deployment, delete_deployment, scale_deployment


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
            call(depl1.metadata.name, "fake_ns", ANY),
            call(depl2.metadata.name, "fake_ns", ANY)
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
