# -*- coding: utf-8 -*-
import io
from unittest.mock import MagicMock, patch, ANY
import urllib3

from chaoslib.exceptions import FailedActivity
from kubernetes import client, config
import pytest

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
    v1.delete_namespaced_pod.assert_called_with(
        pod.metadata.name, "default", ANY)


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

    with pytest.raises(FailedActivity) as x:
        assert pods_in_phase(
            label_selector="app=mysvc", phase="Running") is True
    assert "pod 'app=mysvc' is in phase 'Pending' but should be "\
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
