from unittest.mock import ANY, MagicMock, call, patch

import pytest
import urllib3
from chaoslib.exceptions import ActivityFailed
from kubernetes.client import V1DaemonSet, V1DaemonSetList
from kubernetes.client.models import V1ObjectMeta

from chaosk8s.daemonset.actions import (
    create_daemon_set,
    delete_daemon_set,
    update_daemon_set,
)
from chaosk8s.daemonset.probes import (
    daemon_set_available_and_healthy,
    daemon_set_fully_available,
    daemon_set_not_fully_available,
    daemon_set_partially_available,
)


@patch("chaosk8s.has_local_config_file", autospec=True)
def test_cannot_process_other_than_yaml_and_json(has_conf):
    has_conf.return_value = False
    path = "./tests/fixtures/invalid-k8s.txt"
    with pytest.raises(ActivityFailed) as excinfo:
        create_daemon_set(spec_path=path)
    assert f"cannot process {path}" in str(excinfo)


@patch("builtins.open", autospec=True)
@patch("chaosk8s.daemonset.actions.json", autospec=True)
@patch("chaosk8s.daemonset.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.daemonset.actions.client", autospec=True)
def test_create_daemon_set(client, api, json, open):
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1
    json.loads.return_value = {"Kind": "Deployment"}

    create_daemon_set(spec_path="depl.json")

    v1.create_namespaced_daemon_set.assert_called_with(
        ANY, body=json.loads.return_value
    )


@patch("chaosk8s.daemonset.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.daemonset.actions.client", autospec=True)
def test_delete_deployment(client, api):
    depl1 = V1DaemonSet(metadata=V1ObjectMeta(name="depl1"))
    depl2 = V1DaemonSet(metadata=V1ObjectMeta(name="depl2"))
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1
    v1.list_namespaced_daemon_set.return_value = V1DaemonSetList(items=(depl1, depl2))

    delete_daemon_set("fake_name", "fake_ns")

    v1.list_namespaced_daemon_set.assert_called_with(
        "fake_ns", field_selector="metadata.name=fake_name"
    )
    v1.delete_namespaced_daemon_set.assert_has_calls(
        calls=[
            call(depl1.metadata.name, "fake_ns", body=ANY),
            call(depl2.metadata.name, "fake_ns", body=ANY),
        ],
        any_order=True,
    )


@patch("chaosk8s.daemonset.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.daemonset.actions.client", autospec=True)
def test_update_daemon_set(client, api):
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1
    spec = {
        "spec": {
            "containers": [
                {
                    "image": "foobar:latest",
                },
            ],
        },
    }
    update_daemon_set("fake", spec, "fake_ns")

    v1.patch_namespaced_daemon_set.assert_called_with(
        name="fake", namespace="fake_ns", body=spec
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.daemonset.probes.watch", autospec=True)
@patch("chaosk8s.daemonset.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_daemon_set_is_fully_available_when_it_should_not(cl, client, watch, has_conf):
    has_conf.return_value = False
    daemonset = MagicMock()
    daemonset.status.desired_number_scheduled = 2
    daemonset.status.number_ready = 1

    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = urllib3.exceptions.ReadTimeoutError(None, None, None)
    watch.Watch.return_value = watcher

    assert daemon_set_not_fully_available("mysvc") is False


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.daemonset.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_expecting_a_healthy_daemon_set_should_be_reported_when_not(
    cl, client, has_conf
):
    has_conf.return_value = False
    result = MagicMock()
    result.items = []

    v1 = MagicMock()
    v1.list_namespaced_daemon_set.return_value = result
    client.AppsV1Api.return_value = v1

    assert daemon_set_available_and_healthy("mysvc") is False

    daemonset = MagicMock()
    daemonset.status.desired_number_scheduled = 2
    daemonset.status.number_ready = 1
    result.items.append(daemonset)

    v1.list_namespaced_daemon_set.return_value = result
    client.AppsV1Api.return_value = v1

    assert daemon_set_available_and_healthy("mysvc") is False


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.daemonset.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_expecting_a_healthy_daemon_set(cl, client, has_conf):
    has_conf.return_value = False
    result = MagicMock()
    result.items = []

    v1 = MagicMock()
    v1.list_namespaced_daemonset.return_value = result
    client.AppsV1Api.return_value = v1

    daemonset = MagicMock()
    daemonset.status.desired_number_scheduled = 2
    daemonset.status.number_ready = 2
    result.items.append(daemonset)

    assert daemon_set_available_and_healthy("mysvc") is True


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.daemonset.probes.watch", autospec=True)
@patch("chaosk8s.daemonset.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_daemon_set_is_fully_available(cl, client, watch, has_conf):
    has_conf.return_value = False
    daemonset = MagicMock()
    daemonset.status.desired_number_scheduled = 2
    daemonset.status.number_ready = 2

    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = [[{"object": daemonset, "type": "ADDED"}]]
    watch.Watch.return_value = watcher

    assert daemon_set_fully_available("mysvc") is True


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.daemonset.probes.watch", autospec=True)
@patch("chaosk8s.daemonset.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_daemon_set_is_not_fully_available_when_it_should(cl, client, watch, has_conf):
    has_conf.return_value = False
    daemonset = MagicMock()
    daemonset.status.desired_number_scheduled = 2
    daemonset.status.number_ready = 0

    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = [[{"object": daemonset, "type": "ADDED"}]]
    watch.Watch.return_value = watcher

    assert daemon_set_fully_available("mysvc") is False


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.daemonset.probes.watch", autospec=True)
@patch("chaosk8s.daemonset.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_daemon_set_is_not_fully_available(cl, client, watch, has_conf):
    has_conf.return_value = False
    result = MagicMock()
    result.items = []

    v1 = MagicMock()
    v1.list_namespaced_daemon_set.return_value = result
    client.AppsV1Api.return_value = v1

    daemonset = MagicMock()
    daemonset.status.desired_number_scheduled = 2
    daemonset.status.number_ready = 1
    result.items.append(daemonset)
    watcher = MagicMock()
    watcher.stream = MagicMock()
    watcher.stream.side_effect = [[{"object": daemonset, "type": "ADDED"}]]
    watch.Watch.return_value = watcher

    assert daemon_set_partially_available("mysvc") is True
    assert daemon_set_not_fully_available("mysvc") is True
