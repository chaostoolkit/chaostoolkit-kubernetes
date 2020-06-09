# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch, ANY

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.statefulset.actions import scale_statefulset, \
    remove_statefulset, create_statefulset
from chaosk8s.statefulset.probes import wait_to_be_healthy


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.statefulset.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_scale_statefulset(cl, client, has_conf):
    has_conf.return_value = False

    body = {"spec": {"replicas": 0}}

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    scale_statefulset(name="my-statefulset", replicas=0)

    assert v1.patch_namespaced_stateful_set.call_count == 1
    v1.patch_namespaced_stateful_set.assert_called_with(
        "my-statefulset", namespace="default", body=body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.statefulset.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_removing_statefulset_with_name(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    result = MagicMock()
    result.items = [MagicMock()]
    result.items[0].metadata.name = "mystatefulset"
    v1.list_namespaced_stateful_set.return_value = result

    remove_statefulset("mystatefulset")

    assert v1.delete_namespaced_stateful_set.call_count == 1
    v1.delete_namespaced_stateful_set.assert_called_with(
        "mystatefulset", "default", body=ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.statefulset.actions.client', autospec=True)
@patch('chaosk8s.client')
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
    remove_statefulset("mystatefulset", label_selector=label_selector)

    assert v1.delete_namespaced_stateful_set.call_count == 1
    v1.delete_namespaced_stateful_set.assert_called_with(
        "mystatefulset", "default", body=ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.statefulset.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_creating_statefulset_with_file_json(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    create_statefulset("tests/fixtures/statefulset/create/file.json")

    assert v1.create_namespaced_stateful_set.call_count == 1
    v1.create_namespaced_stateful_set.assert_called_with(
        "default", body=body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.statefulset.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_creating_statefulset_with_file_yaml(cl, client, has_conf):
    has_conf.return_value = False

    body = "example of body"

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    create_statefulset("tests/fixtures/statefulset/create/file.yaml")

    assert v1.create_namespaced_stateful_set.call_count == 1
    v1.create_namespaced_stateful_set.assert_called_with(
        "default", body=body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.statefulset.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_creating_statefulset_with_file_txt_KO(cl, client, has_conf):
    has_conf.return_value = False

    path = "tests/fixtures/statefulset/create/file.txt"

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        create_statefulset(path)
    assert "cannot process {path}".format(path=path) in str(excinfo.value)


@patch('chaosk8s.statefulset.probes.client', autospec=True)
def test_wait_to_be_healthy_should_wait_for_replicas_to_match(client):
    read_count = 0
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    def read_namespaced_stateful_set(name, ns):
        nonlocal read_count
        read_count = read_count+1
        statefulset = MagicMock()
        statefulset.spec.replicas = 2
        statefulset.status.ready_replicas = read_count
        return statefulset

    v1.read_namespaced_stateful_set = read_namespaced_stateful_set

    wait_to_be_healthy(
        name="statefulset",
        timeout_secs=3,
        interval_secs=1
    )

    assert read_count == 2


@patch('chaosk8s.statefulset.probes.client', autospec=True)
def test_wait_to_be_healthy_should_fail_if_replicas_dont_match(client):
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    def read_namespaced_stateful_set(name, ns):
        statefulset = MagicMock()
        statefulset.spec.replicas = 2
        statefulset.status.ready_replicas = 0
        return statefulset

    v1.read_namespaced_stateful_set = read_namespaced_stateful_set

    with pytest.raises(ActivityFailed) as exception:
        wait_to_be_healthy(
            name="statefulset",
            timeout_secs=3,
            interval_secs=1
        )

    assert "failed to reach a healthy state" in str(exception)
