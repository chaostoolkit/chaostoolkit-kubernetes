from unittest.mock import MagicMock, patch

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.namespace.actions import create_namespace, delete_namespace
from chaosk8s.namespace.probes import namespace_exists


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.namespace.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_namespace_with_name(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1
    name = "foobar"
    ns = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": name}}

    create_namespace(name)

    assert v1.create_namespace.call_count == 1
    v1.create_namespace.assert_called_with(body=ns)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.namespace.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_namespace_with_file_json(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_namespace(spec_path="tests/fixtures/service/create/file.json")

    assert v1.create_namespace.call_count == 1
    v1.create_namespace.assert_called_with(body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.namespace.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_namespace_with_file_yaml(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    create_namespace(spec_path="tests/fixtures/namespace/create/file.yaml")

    assert v1.create_namespace.call_count == 1
    v1.create_namespace.assert_called_with(body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.namespace.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_namespace_with_file_txt_KO(cl, client, has_conf):
    has_conf.return_value = False

    path = "tests/fixtures/service/create/file.txt"

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        create_namespace(spec_path=path)
    assert f"cannot process {path}" in str(excinfo.value)


@patch("chaosk8s.namespace.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.namespace.actions.client", autospec=True)
def test_delete_namespace(client, api):
    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    delete_namespace("fake")

    v1.delete_namespace.assert_called_with("fake")


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.namespace.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_namespace_exists(cl, client, has_conf):
    has_conf.return_value = False
    namespace = MagicMock()
    result = MagicMock()
    result.items = [namespace]

    v1 = MagicMock()
    v1.list_namespace.return_value = result
    client.CoreV1Api.return_value = v1

    assert namespace_exists("mynamespace") is True
    v1.list_namespace.assert_called_with(field_selector="metadata.name=mynamespace")
