# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch, ANY, call

from kubernetes import client

import pytest
from chaoslib.exceptions import ActivityFailed

from chaosk8s.pod.actions import terminate_pods
from chaosk8s.pod.probes import pods_in_phase, pods_not_in_phase


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_name_pattern(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.metadata.name = "my-app-1"

    pod2 = MagicMock()
    pod2.metadata.name = "some-db"

    result = MagicMock()
    result.items = [pod, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods(name_pattern="my-app-[0-9]$")

    assert v1.delete_namespaced_pod.call_count == 1
    v1.delete_namespaced_pod.assert_called_with(
        pod.metadata.name, "default", ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_name_pattern_all(cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"

    pod3 = MagicMock()
    pod3.metadata.name = "my-app-test-3"

    result = MagicMock()
    result.items = [pod1, pod2, pod3]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods(name_pattern="my-app-[0-9]$", all=True)

    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", ANY),
             call(pod2.metadata.name, "default", ANY)]
    v1.delete_namespaced_pod.assert_has_calls(calls, any_order=True)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_name_pattern_rand(cl, client, has_conf):
    # Patch `random.sample` to always return last items in seq
    with patch('random.sample', side_effect=lambda seq, qty: seq[-qty:]):
        has_conf.return_value = False
        pod1 = MagicMock()
        pod1.metadata.name = "my-app-1"

        pod2 = MagicMock()
        pod2.metadata.name = "my-app-2"

        pod3 = MagicMock()
        pod3.metadata.name = "my-app-3"

        pod4 = MagicMock()
        pod4.metadata.name = "my-app-test-1"

        result = MagicMock()
        result.items = [pod1, pod2, pod3, pod4]

        v1 = MagicMock()
        v1.list_namespaced_pod.return_value = result
        client.CoreV1Api.return_value = v1

        terminate_pods(name_pattern="my-app-[0-9]$", rand=True)

        assert v1.delete_namespaced_pod.call_count == 1
        v1.delete_namespaced_pod.assert_called_with(
            pod3.metadata.name, "default", ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_all(cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-app"

    pod2 = MagicMock()
    pod2.metadata.name = "some-db"

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods(all=True)

    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", ANY),
             call(pod2.metadata.name, "default", ANY)]
    v1.delete_namespaced_pod.assert_has_calls(calls, any_order=True)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_rand(cl, client, has_conf):
    # Patch `random.sample` to always return last items in seq
    with patch('random.sample', side_effect=lambda seq, qty: seq[-qty:]):
        has_conf.return_value = False
        pod1 = MagicMock()
        pod1.metadata.name = "some-app"

        pod2 = MagicMock()
        pod2.metadata.name = "some-db"

        result = MagicMock()
        result.items = [pod1, pod2]

        v1 = MagicMock()
        v1.list_namespaced_pod.return_value = result
        client.CoreV1Api.return_value = v1

        terminate_pods(rand=True)

        assert v1.delete_namespaced_pod.call_count == 1
        v1.delete_namespaced_pod.assert_called_with(
            pod2.metadata.name, "default", ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_when_no_params_given(cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-app"

    pod2 = MagicMock()
    pod2.metadata.name = "some-db"

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods()

    assert v1.delete_namespaced_pod.call_count == 1
    v1.delete_namespaced_pod.assert_called_with(
        pod1.metadata.name, "default", ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_when_grace_period_is_set(cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-app"

    result = MagicMock()
    result.items = [pod1]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods(grace_period = 5)

    assert v1.delete_namespaced_pod.call_count == 1
    v1.delete_namespaced_pod.assert_called_with(
        pod1.metadata.name, "default", client.V1DeleteOptions(grace_period_seconds = 5))


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_given_percentage(cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-app-1"

    pod2 = MagicMock()
    pod2.metadata.name = "some-db-1"

    pod3 = MagicMock()
    pod3.metadata.name = "some-app-2"

    pod4 = MagicMock()
    pod4.metadata.name = "some-db-2"

    result = MagicMock()
    result.items = [pod1, pod2, pod3, pod4]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods(mode='percentage', qty=40)

    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", ANY),
             call(pod2.metadata.name, "default", ANY)]
    v1.delete_namespaced_pod.assert_has_calls(calls, any_order=True)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_given_percentage_rand(cl, client, has_conf):
    # Patch `random.sample` to always return last items in seq
    with patch('random.sample', side_effect=lambda seq, qty: seq[-qty:]):
        has_conf.return_value = False
        pod1 = MagicMock()
        pod1.metadata.name = "some-app-1"

        pod2 = MagicMock()
        pod2.metadata.name = "some-db-1"

        pod3 = MagicMock()
        pod3.metadata.name = "some-app-2"

        pod4 = MagicMock()
        pod4.metadata.name = "some-db-2"

        result = MagicMock()
        result.items = [pod1, pod2, pod3, pod4]

        v1 = MagicMock()
        v1.list_namespaced_pod.return_value = result
        client.CoreV1Api.return_value = v1

        terminate_pods(mode='percentage', qty=40, rand=True)

        assert v1.delete_namespaced_pod.call_count == 2
        calls = [call(pod3.metadata.name, "default", ANY),
                 call(pod4.metadata.name, "default", ANY)]
        v1.delete_namespaced_pod.assert_has_calls(calls, any_order=True)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_when_qty_grt_than_pods_selected(cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-app"

    pod2 = MagicMock()
    pod2.metadata.name = "some-db"

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods(qty=40)

    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", ANY),
             call(pod2.metadata.name, "default", ANY)]
    v1.delete_namespaced_pod.assert_has_calls(calls, any_order=True)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_should_fail_when_qty_less_than_pods_selected(
        cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-app"

    pod2 = MagicMock()
    pod2.metadata.name = "some-db"

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        terminate_pods(qty=-4)
    assert "Cannot terminate pods. Quantity '-4' is negative." in str(excinfo)
    assert v1.delete_namespaced_pod.call_count == 0


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_should_fail_when_mode_not_present(
        cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-app"

    pod2 = MagicMock()
    pod2.metadata.name = "some-db"

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as expinfo:
        terminate_pods(mode="some_mode")
    assert "Cannot terminate pods. " \
           "Mode 'some_mode' is invalid." in str(expinfo)
    assert v1.delete_namespaced_pod.call_count == 0


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_pods_in_phase(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status = MagicMock()
    pod.status.phase = "Running"
    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    assert pods_in_phase(label_selector="app=mysvc", phase="Running") is True


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_pods_should_have_been_phase(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status = MagicMock()
    pod.status.phase = "Pending"
    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as x:
        assert pods_in_phase(
            label_selector="app=mysvc", phase="Running") is True
    assert "pod 'app=mysvc' is in phase 'Pending' but should be " \
           "'Running'" in str(x)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_pods_not_in_phase(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status = MagicMock()
    pod.status.phase = "Pending"
    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    assert pods_not_in_phase(
        label_selector="app=mysvc", phase="Running") is True
