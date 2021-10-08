# -*- coding: utf-8 -*-
from unittest.mock import ANY, MagicMock, patch

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.service.actions import create_service_endpoint, delete_service
from chaosk8s.service.probes import service_is_initialized


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.service.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_service_endpoint_with_file_json(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_service_endpoint("tests/fixtures/service/create/file.json")

    assert v1.create_namespaced_service.call_count == 1
    v1.create_namespaced_service.assert_called_with("default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.service.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_service_endpoint_with_file_yaml(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_service_endpoint("tests/fixtures/service/create/file.yaml")

    assert v1.create_namespaced_service.call_count == 1
    v1.create_namespaced_service.assert_called_with("default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.service.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_service_endpoint_with_file_txt_KO(cl, client, has_conf):
    has_conf.return_value = False

    path = "tests/fixtures/service/create/file.txt"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        create_service_endpoint(path)
    assert "cannot process {path}".format(path=path) in str(excinfo.value)


@patch("chaosk8s.service.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.service.actions.client", autospec=True)
def test_delete_service(client, api):
    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    delete_service("fake", "fake_ns")

    v1.delete_namespaced_service.assert_called_with("fake", namespace="fake_ns")


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.service.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_expecting_service_should_be_initialized(cl, client, has_conf):
    has_conf.return_value = False
    service = MagicMock()
    result = MagicMock()
    result.items = [service]

    v1 = MagicMock()
    v1.list_namespaced_service.return_value = result
    client.CoreV1Api.return_value = v1

    assert service_is_initialized("mysvc") is True
    v1.list_namespaced_service.assert_called_with(
        "default", field_selector="metadata.name=mysvc"
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.service.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_can_select_by_label(cl, client, has_conf):
    has_conf.return_value = False
    result = MagicMock()
    result.items = [MagicMock()]

    v1 = MagicMock()
    v1.list_namespaced_service.return_value = result
    client.CoreV1Api.return_value = v1

    label_selector = "app=my-super-app"
    service_is_initialized("mysvc", label_selector=label_selector)
    v1.list_namespaced_service.assert_called_with(
        "default", field_selector="metadata.name=mysvc", label_selector=label_selector
    )
