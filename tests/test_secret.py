from unittest.mock import MagicMock, patch

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.secret.actions import create_secret, delete_secret
from chaosk8s.secret.probes import secret_exists


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.secret.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_secret_with_file_json(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_secret("tests/fixtures/service/create/file.json")

    assert v1.create_namespaced_secret.call_count == 1
    v1.create_namespaced_secret.assert_called_with("default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.secret.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_secret_with_file_yaml(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_secret("tests/fixtures/secret/create/file.yaml")

    assert v1.create_namespaced_secret.call_count == 1
    v1.create_namespaced_secret.assert_called_with("default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.secret.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_secret_with_file_txt_KO(cl, client, has_conf):
    has_conf.return_value = False

    path = "tests/fixtures/service/create/file.txt"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        create_secret(path)
    assert f"cannot process {path}" in str(excinfo.value)


@patch("chaosk8s.secret.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.secret.actions.client", autospec=True)
def test_delete_secret(client, api):
    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    delete_secret("fake", "fake_ns")

    v1.delete_namespaced_secret.assert_called_with("fake", namespace="fake_ns")


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.secret.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_expecting_service_should_be_initialized(cl, client, has_conf):
    has_conf.return_value = False
    secret = MagicMock()
    result = MagicMock()
    result.items = [secret]

    v1 = MagicMock()
    v1.list_namespaced_secret.return_value = result
    client.CoreV1Api.return_value = v1

    assert secret_exists("mysecret") is True
    v1.list_namespaced_secret.assert_called_with(
        "default", field_selector="metadata.name=mysecret"
    )
