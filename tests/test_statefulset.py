from unittest.mock import ANY, MagicMock, patch

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.statefulset.actions import (
    create_statefulset,
    remove_statefulset,
    scale_statefulset,
)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.statefulset.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_scale_statefulset(cl, client, has_conf):
    has_conf.return_value = False

    body = {"spec": {"replicas": 0}}

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    scale_statefulset(name="my-statefulset", replicas=0)

    assert v1.patch_namespaced_stateful_set.call_count == 1
    v1.patch_namespaced_stateful_set.assert_called_with(
        "my-statefulset", namespace="default", body=body
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.statefulset.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_removing_statefulset_with_name(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    result = MagicMock()
    result.items = [MagicMock()]
    result.items[0].metadata.name = "mystatefulset"
    v1.list_namespaced_stateful_set.return_value = result

    remove_statefulset("mystatefulset")

    v1.list_namespaced_stateful_set.assert_called_with(
        "default", field_selector="metadata.name=mystatefulset"
    )
    assert v1.delete_namespaced_stateful_set.call_count == 1
    v1.delete_namespaced_stateful_set.assert_called_with(
        "mystatefulset", "default", body=ANY
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.statefulset.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_removing_statefulset_with_label_selector(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    result = MagicMock()
    result.items = [MagicMock()]
    result.items[0].metadata.name = "mystatefulset"
    result.items[0].metadata.labels.app = "my-super-app"
    v1.list_namespaced_stateful_set.return_value = result

    label_selector = "app=my-super-app"
    remove_statefulset(label_selector=label_selector)

    v1.list_namespaced_stateful_set.assert_called_with(
        "default", label_selector=label_selector
    )
    assert v1.delete_namespaced_stateful_set.call_count == 1
    v1.delete_namespaced_stateful_set.assert_called_with(
        "mystatefulset", "default", body=ANY
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.statefulset.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_statefulset_with_file_json(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    create_statefulset("tests/fixtures/statefulset/create/file.json")

    assert v1.create_namespaced_stateful_set.call_count == 1
    v1.create_namespaced_stateful_set.assert_called_with("default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.statefulset.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_statefulset_with_file_yaml(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    create_statefulset("tests/fixtures/statefulset/create/file.yaml")

    assert v1.create_namespaced_stateful_set.call_count == 1
    v1.create_namespaced_stateful_set.assert_called_with("default", body=body)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.statefulset.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_statefulset_with_file_txt_KO(cl, client, has_conf):
    has_conf.return_value = False

    path = "tests/fixtures/statefulset/create/file.txt"

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        create_statefulset(path)
    assert f"cannot process {path}" in str(excinfo.value)
