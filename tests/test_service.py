# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch, ANY

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.service.actions import create_service_endpoint


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.service.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_creating_service_endpoint_with_file_json(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_service_endpoint("tests/fixtures/service/create/file.json")

    assert v1.create_namespaced_service.call_count == 1
    v1.create_namespaced_service.assert_called_with(
        "default", body=body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.service.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_creating_service_endpoint_with_file_yaml(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_service_endpoint("tests/fixtures/service/create/file.yaml")

    assert v1.create_namespaced_service.call_count == 1
    v1.create_namespaced_service.assert_called_with(
        "default", body=body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.service.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_creating_service_endpoint_with_file_txt_KO(cl, client, has_conf):
    has_conf.return_value = False

    path = "tests/fixtures/service/create/file.txt"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        create_service_endpoint(path)
    assert "cannot process {path}".format(path=path) in str(excinfo.value)