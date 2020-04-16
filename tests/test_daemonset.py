# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch, ANY, call

import pytest
from kubernetes import stream
from chaoslib.exceptions import ActivityFailed, InvalidActivity
from chaoslib.provider.python import validate_python_activity

from chaosk8s.daemonset.probes import daemonset_ready


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.daemonset.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_daemonset_ready(cl, client, has_conf):
    has_conf.return_value = False

    ds = MagicMock()
    ds.status.number_unavailable = None
    ds.status.number_misscheduled = 0
    result = MagicMock()
    result.items = [ds,ds]

    v1 = MagicMock()
    v1.list_namespaced_daemon_set.return_value = result
    client.AppsV1Api.return_value = v1

    assert daemonset_ready("test")


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.daemonset.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_daemonset_not_ready(cl, client, has_conf):
    has_conf.return_value = False

    ds = MagicMock()
    ds.status.number_unavailable = 1
    ds.status.number_misscheduled = 0
    result = MagicMock()
    result.items = [ds,ds]

    v1 = MagicMock()
    v1.list_namespaced_daemon_set.return_value = result
    client.AppsV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as excinfo:
        daemonset_ready("test")
    assert "DaemonSet has '1' unavailable replicas and '0' misscheduled" in str(excinfo.value)

@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.daemonset.probes.client', autospec=True)
@patch('chaosk8s.client')
def test_daemonset_ready_not_found(cl, client, has_conf):
    has_conf.return_value = False
    result = MagicMock()
    result.items = []

    v1 = MagicMock()
    v1.list_namespaced_daemon_set.return_value = result
    client.AppsV1Api.return_value = v1

    name = "test"
    with pytest.raises(ActivityFailed) as excinfo:
        daemonset_ready(name)
    assert "DaemonSet '{name}' was not found".format(name=name) in str(excinfo.value)