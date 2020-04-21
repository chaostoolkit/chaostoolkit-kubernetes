# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch, ANY, call

import pytest
from kubernetes import stream
from chaoslib.exceptions import ActivityFailed, InvalidActivity
from chaoslib.provider.python import validate_python_activity

from chaosk8s.pod.actions import terminate_pods, exec_in_pods
from chaosk8s.pod.probes import pods_in_phase, pods_not_in_phase, \
    pods_in_conditions, all_pods_healthy


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

    ret = terminate_pods(name_pattern="my-app-[0-9]$")
    
    assert len(ret) == 1
    assert ret == [pod.metadata.name]
    assert v1.delete_namespaced_pod.call_count == 1
    v1.delete_namespaced_pod.assert_called_with(
        pod.metadata.name, "default", body=ANY)


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

    ret = terminate_pods(name_pattern="my-app-[0-9]$", all=True)

    assert len(ret) == 2
    assert ret == [pod1.metadata.name, pod2.metadata.name]
    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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

        ret = terminate_pods(name_pattern="my-app-[0-9]$", rand=True)

        assert len(ret) == 1
        assert ret == [pod3.metadata.name]
        assert v1.delete_namespaced_pod.call_count == 1
        v1.delete_namespaced_pod.assert_called_with(
            pod3.metadata.name, "default", body=ANY)


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

    ret = terminate_pods(all=True)

    assert len(ret) == 2
    assert ret == [pod1.metadata.name, pod2.metadata.name]
    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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

        ret = terminate_pods(rand=True)

        assert len(ret) == 1
        assert ret == [pod2.metadata.name]
        assert v1.delete_namespaced_pod.call_count == 1
        v1.delete_namespaced_pod.assert_called_with(
            pod2.metadata.name, "default", body=ANY)


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

    ret = terminate_pods()

    assert len(ret) == 1
    assert ret == [pod1.metadata.name]
    assert v1.delete_namespaced_pod.call_count == 1
    v1.delete_namespaced_pod.assert_called_with(
        pod1.metadata.name, "default", body=ANY)


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

    ret = terminate_pods(grace_period=5)

    assert len(ret) == 1
    assert ret == [pod1.metadata.name]
    assert v1.delete_namespaced_pod.call_count == 1
    v1.delete_namespaced_pod.assert_called_with(
        pod1.metadata.name, "default",
        body=client.V1DeleteOptions(grace_period_seconds=5))


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

    ret = terminate_pods(mode='percentage', qty=40)

    assert len(ret) == 2
    assert ret == [pod1.metadata.name, pod2.metadata.name]
    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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

        ret = terminate_pods(mode='percentage', qty=40, rand=True)

        assert len(ret) == 2
        assert ret == [pod3.metadata.name, pod4.metadata.name]
        assert v1.delete_namespaced_pod.call_count == 2
        calls = [call(pod3.metadata.name, "default", body=ANY),
                 call(pod4.metadata.name, "default", body=ANY)]
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

    ret = terminate_pods(qty=40)

    assert len(ret) == 2
    assert ret == [pod1.metadata.name, pod2.metadata.name]
    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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
    assert "Cannot select pods. Quantity '-4' is negative." in \
        str(excinfo.value)
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
    assert "Cannot select pods. " \
           "Mode 'some_mode' is invalid." in str(expinfo.value)
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
           "'Running'" in str(x.value)


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


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_pods_in_conditions(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status = MagicMock()
    pod.status.conditions = [MagicMock()]
    pod.status.conditions[0].type = "Ready"
    pod.status.conditions[0].status = "True"
    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    # assert it works in the nominal case
    assert pods_in_conditions(
        label_selector="app=mysvc",
        conditions=[
            {
                "type": "Ready",
                "status": "True"
            }
        ]
    ) is True

    # assert it works even if the hash is not in the same order
    # (just in case we add an ordered dict for some reason)
    assert pods_in_conditions(
        label_selector="app=mysvc",
        conditions=[
            {
                "status": "True",
                "type": "Ready"
            }
        ]
    ) is True

    # assert it does not work when the condition is present but does not match
    with pytest.raises(ActivityFailed) as excinfo:
        pods_in_conditions(
            label_selector="app=mysvc",
            conditions=[
                {
                    "status": "False",
                    "type": "Ready"
                }
            ]
        )
    assert str(excinfo)

    # assert it does not work when the condition is absent
    with pytest.raises(ActivityFailed) as excinfo:
        pods_in_conditions(
            label_selector="app=mysvc",
            conditions=[
                {
                    "status": "True",
                    "type": "PodScheduled"
                }
            ]
        )
    assert str(excinfo)


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
        pod.metadata.name, "default", body=ANY)


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
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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
            pod3.metadata.name, "default", body=ANY)


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
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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
            pod2.metadata.name, "default", body=ANY)


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
        pod1.metadata.name, "default", body=ANY)


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

    terminate_pods(grace_period=5)

    assert v1.delete_namespaced_pod.call_count == 1
    v1.delete_namespaced_pod.assert_called_with(
        pod1.metadata.name, "default",
        body=client.V1DeleteOptions(grace_period_seconds=5))


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
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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
        calls = [call(pod3.metadata.name, "default", body=ANY),
                 call(pod4.metadata.name, "default", body=ANY)]
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
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
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
    assert "Cannot select pods. Quantity '-4' is negative." in \
        str(excinfo.value)
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
    assert "Cannot select pods. " \
           "Mode 'some_mode' is invalid." in str(expinfo.value)
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
           "'Running'" in str(x.value)


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


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_pods_in_conditions(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status = MagicMock()
    pod.status.conditions = [MagicMock()]
    pod.status.conditions[0].type = "Ready"
    pod.status.conditions[0].status = "True"
    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    # assert it works in the nominal case
    assert pods_in_conditions(
        label_selector="app=mysvc",
        conditions=[
            {
                "type": "Ready",
                "status": "True"
            }
        ]
    ) is True

    # assert it works even if the hash is not in the same order
    # (just in case we add an ordered dict for some reason)
    assert pods_in_conditions(
        label_selector="app=mysvc",
        conditions=[
            {
                "status": "True",
                "type": "Ready"
            }
        ]
    ) is True

    # assert it does not work when the condition is present but does not match
    with pytest.raises(ActivityFailed) as excinfo:
        pods_in_conditions(
            label_selector="app=mysvc",
            conditions=[
                {
                    "status": "False",
                    "type": "Ready"
                }
            ]
        )
    assert str(excinfo)

    # assert it does not work when the condition is absent
    with pytest.raises(ActivityFailed) as excinfo:
        pods_in_conditions(
            label_selector="app=mysvc",
            conditions=[
                {
                    "status": "True",
                    "type": "PodScheduled"
                }
            ]
        )
    assert str(excinfo)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_by_name_pattern(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"
    container2 = MagicMock()
    container2.name = "container2"

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    pod3 = MagicMock()
    pod3.metadata.name = "my-app-a"
    pod3.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1, pod2, pod3]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    stream.stream.return_value.read_channel = MagicMock()
    stream.stream.return_value.read_channel.return_value = '{"status":"Success"}'

    exec_in_pods(name_pattern="my-app-[0-9]$",
                 cmd="dummy -a -b -c",
                 container_name="container1",
                 all=True)

    assert stream.stream.call_count == 2


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_by_name_pattern_rand(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"
    container2 = MagicMock()
    container2.name = "container2"

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    pod3 = MagicMock()
    pod3.metadata.name = "my-app-3"
    pod3.spec.containers = [container1, container2]

    pod4 = MagicMock()
    pod4.metadata.name = "my-app-test-1"
    pod4.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1, pod2, pod3, pod4]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    stream.stream.return_value.read_channel = MagicMock()
    stream.stream.return_value.read_channel.return_value = '{"status":"Success"}'

    exec_in_pods(name_pattern="my-app-[0-9]$",
                 cmd="dummy -a -b -c",
                 container_name="container2",
                 qty=3,
                 rand=True)

    assert stream.stream.call_count == 3


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_unhealthy_system_should_be_reported(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.status.phase = "Failed"

    result = MagicMock()
    result.items = [pod]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    stream.stream.return_value.read_channel = MagicMock()
    stream.stream.return_value.read_channel.return_value = '{"status":"Success"}'

    with pytest.raises(ActivityFailed) as excinfo:
        all_pods_healthy()
    assert "the system is unhealthy" in str(excinfo.value)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_invalid_container_name(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"
    container2 = MagicMock()
    container2.name = "container2"

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    exec_in_pods(name_pattern="my-app-[0-9]$",
                 cmd="dummy -a -b -c",
                 container_name="bad_container_name",
                 qty=2,
                 rand=True)

    assert stream.stream.call_count == 0


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_no_command_provided(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"
    container2 = MagicMock()
    container2.name = "container2"

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()

    with pytest.raises(InvalidActivity) as expinfo:
        validate_python_activity({
            "name": "run-in-pod",
            "type": "action",
            "provider": {
                "type": "python",
                "module": "chaosk8s.pod.actions",
                "func": "exec_in_pods",
                "arguments": dict(
                    name_pattern="my-app-[0-9]$",
                    container_name="container1",
                    qty=2,
                    rand=True
                )
            }
        })

    with pytest.raises(ActivityFailed) as expinfo:
        exec_in_pods(
            cmd=None,
            name_pattern="my-app-[0-9]$",
            container_name="container1",
            qty=2,
            rand=True
        )

    assert "A command must be set to run a container" in str(expinfo.value)
    assert stream.stream.call_count == 0


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_no_pod_found_with_name(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"
    container2 = MagicMock()
    container2.name = "container2"

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    exec_in_pods(name_pattern="no-app-[0-9]$",
                 cmd="dummy -a -b -c",
                 container_name="container1",
                 qty=2,
                 rand=True)

    assert stream.stream.call_count == 0


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_order_by_oldest(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"
    container2 = MagicMock()
    container2.name = "container2"

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.metadata.creation_timestamp = "2019-11-25T13:50:31Z"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.metadata.creation_timestamp = "2019-11-25T13:55:00Z"
    pod2.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    stream.stream.return_value.read_channel = MagicMock()
    stream.stream.return_value.read_channel.return_value = '{"status":"Success"}'

    exec_in_pods(name_pattern="my-app-[0-9]$",
                 order="oldest",
                 cmd="dummy -a -b -c",
                 container_name="container1",
                 qty=2,
                 rand=True)

    assert stream.stream.call_count == 2


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_invalid_order(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"
    container2 = MagicMock()
    container2.name = "container2"

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1, pod2]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1
    stream.stream = MagicMock()
    with pytest.raises(ActivityFailed) as excinfo:
        exec_in_pods(name_pattern="my-app-[0-9]$",
                     order="bad_order",
                     cmd="dummy -a -b -c",
                     container_name="container1",
                     qty=2,
                     rand=True)
    assert "Cannot select pods. Order 'bad_order' is invalid." in  str(excinfo.value)
    assert stream.stream.call_count == 0


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_using_pod_label_selector(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"

    container2 = MagicMock()
    container2.name = "container2"
    container2.metadata.labels = {"dummy_label1": "dummy_value1", "dummy_label1": "dummy_value2"}

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    stream.stream.return_value.read_channel = MagicMock()
    stream.stream.return_value.read_channel.return_value = '{"status":"Success"}'

    exec_in_pods(label_selector="dummy_label1=dummy_value1",
                 cmd="dummy -a -b -c",
                 container_name="container1",
                 qty=2,
                 rand=True)
    assert stream.stream.call_count == 1


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_exec_in_pods_return_value(cl, client, has_conf):
    has_conf.return_value = False

    container1 = MagicMock()
    container1.name = "container1"

    container2 = MagicMock()
    container2.name = "container2"
    container2.metadata.labels = {"dummy_label1": "dummy_value1", "dummy_label1": "dummy_value2"}

    pod1 = MagicMock()
    pod1.metadata.name = "my-app-1"
    pod1.spec.containers = [container1, container2]

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"
    pod2.spec.containers = [container1, container2]

    result = MagicMock()
    result.items = [pod1]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    stream.stream = MagicMock()
    stream.stream.return_value.read_channel = MagicMock()
    stream.stream.return_value.read_channel.return_value = '{"status":"Success"}'

    exec_in_pods(label_selector="dummy_label1=dummy_value1",
                 cmd="dummy -a -b -c",
                 container_name="container1",
                 qty=2,
                 rand=True)
    assert stream.stream.call_count == 1


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_succeeded_and_running_pods_should_be_considered_healthy(cl, client,
                                                                 has_conf):
    has_conf.return_value = False

    podSucceeded = MagicMock()
    podSucceeded.status.phase = "Succeeded"

    podRunning = MagicMock()
    podRunning.status.phase = "Running"

    result = MagicMock()
    result.items = [podSucceeded, podRunning]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    health = all_pods_healthy()
    assert health


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_name_with_prefix_pattern(cl, client, has_conf):
    has_conf.return_value = False
    pod = MagicMock()
    pod.metadata.name = "some-random-string-my-app-1"

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
        pod.metadata.name, "default", body=ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_name_with_prefix_pattern_all(cl, client, has_conf):
    has_conf.return_value = False
    pod1 = MagicMock()
    pod1.metadata.name = "some-random-string-my-app-1"

    pod2 = MagicMock()
    pod2.metadata.name = "my-app-2"

    pod3 = MagicMock()
    pod3.metadata.name = "some-random-3-my-app-test-3"

    result = MagicMock()
    result.items = [pod1, pod2, pod3]

    v1 = MagicMock()
    v1.list_namespaced_pod.return_value = result
    client.CoreV1Api.return_value = v1

    terminate_pods(name_pattern="my-app-[0-9]$", all=True)

    assert v1.delete_namespaced_pod.call_count == 2
    calls = [call(pod1.metadata.name, "default", body=ANY),
             call(pod2.metadata.name, "default", body=ANY)]
    v1.delete_namespaced_pod.assert_has_calls(calls, any_order=True)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.pod.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_terminate_pods_by_name_with_prefix_pattern_rand(cl, client, has_conf):
    # Patch `random.sample` to always return last items in seq
    with patch('random.sample', side_effect=lambda seq, qty: seq[-qty:]):
        has_conf.return_value = False
        pod1 = MagicMock()
        pod1.metadata.name = "some-random-1-string-my-app-1"

        pod2 = MagicMock()
        pod2.metadata.name = "my-app-2-with-prefix"

        pod3 = MagicMock()
        pod3.metadata.name = "some-random-3-my-app-3"

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
            pod3.metadata.name, "default", body=ANY)

