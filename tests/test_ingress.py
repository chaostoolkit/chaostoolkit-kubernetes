from unittest.mock import MagicMock, patch

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.networking.actions import create_ingress, delete_ingress, update_ingress
from chaosk8s.networking.probes import ingress_exists


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.networking.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_ingress_with_file_json(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.NetworkingV1Api.return_value = v1

    create_ingress(spec_path="tests/fixtures/service/create/file.json")

    assert v1.create_namespaced_ingress.call_count == 1
    v1.create_namespaced_ingress.assert_called_with(namespace="default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.networking.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_ingress_with_file_yaml(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.NetworkingV1Api.return_value = v1

    create_ingress(spec_path="tests/fixtures/namespace/create/file.yaml")

    assert v1.create_namespaced_ingress.call_count == 1
    v1.create_namespaced_ingress.assert_called_with(namespace="default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.networking.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_ingress_with_file_txt_KO(cl, client, has_conf):
    has_conf.return_value = False

    path = "tests/fixtures/service/create/file.txt"

    v1 = MagicMock()
    client.NetworkingV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        create_ingress(spec_path=path)
    assert f"cannot process {path}" in str(excinfo.value)


@patch("chaosk8s.networking.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.networking.actions.client", autospec=True)
def test_update_ingress(client, api):
    v1 = MagicMock()
    client.NetworkingV1Api.return_value = v1
    spec = {"spec": {"ingress_class_name": "foobar"}}

    update_ingress("fake", spec)

    v1.patch_namespaced_ingress.assert_called_with(
        name="fake", namespace="default", body=spec
    )


@patch("chaosk8s.networking.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.networking.actions.client", autospec=True)
def test_delete_ingress(client, api):
    v1 = MagicMock()
    client.NetworkingV1Api.return_value = v1

    delete_ingress("fake")

    v1.delete_namespaced_ingress.assert_called_with("fake", namespace="default")


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.networking.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_namespace_exists(cl, client, has_conf):
    has_conf.return_value = False
    ingress = MagicMock()
    result = MagicMock()
    result.items = [ingress]

    v1 = MagicMock()
    v1.list_namespaced_ingress.return_value = result
    client.NetworkingV1Api.return_value = v1

    assert ingress_exists("mynamespace") is True
    v1.list_namespaced_ingress.assert_called_with(
        namespace="default", field_selector="metadata.name=mynamespace"
    )
