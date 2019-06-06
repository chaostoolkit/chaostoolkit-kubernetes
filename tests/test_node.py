# -*- coding: utf-8 -*-
from unittest.mock import ANY, MagicMock, patch

import pytest
from chaoslib.exceptions import ActivityFailed
from kubernetes.client.rest import ApiException

from chaosk8s.node.actions import cordon_node, create_node, delete_nodes, \
    uncordon_node, drain_nodes


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_create_node(cl, client, has_conf):
    has_conf.return_value = False

    meta = {
        "cluster_name": "somevalue"
    }

    spec = {
        "external_id": "somemetavalue"
    }

    node = MagicMock()
    node.metadata.name = "mynode"

    v1 = MagicMock()
    v1.create_node.return_value = node
    client.CoreV1Api.return_value = v1

    res = create_node(meta, spec)
    assert res.metadata.name == "mynode"


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_create_node_may_fail(cl, client, has_conf):
    has_conf.return_value = False

    meta = {
        "cluster_name": "somevalue"
    }

    spec = {
        "external_id": "somemetavalue"
    }

    v1 = MagicMock()
    v1.create_node.side_effect = ApiException()
    client.CoreV1Api.return_value = v1

    with pytest.raises(ActivityFailed) as x:
        create_node(meta, spec)
    assert "Creating new node failed" in str(x)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_delete_nodes(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    res = MagicMock()
    res.status = "Success"
    v1.delete_node.return_value = res

    delete_nodes(label_selector="k=mynode")

    v1.delete_node.assert_called_with("mynode", ANY, grace_period_seconds=None)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_cordon_node_by_name(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    cordon_node(name="mynode")

    body = {
        "spec": {
            "unschedulable": True
        }
    }

    v1.patch_node.assert_called_with("mynode", body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_uncordon_node_by_name(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    uncordon_node(name="mynode")

    body = {
        "spec": {
            "unschedulable": False
        }
    }

    v1.patch_node.assert_called_with("mynode", body)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_drain_nodes_by_name(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    owner = MagicMock()
    owner.controller = True
    owner.kind = "ReplicationSet"

    pod = MagicMock()
    pod.metadata.uid = "1"
    pod.metadata.name = "apod"
    pod.metadata.namespace = "default"
    pod.metadata.owner_references = [owner]

    pods = MagicMock()
    pods.items = [pod]
    v1.list_pod_for_all_namespaces.return_value = pods

    new_pod = MagicMock()
    new_pod.metadata.uid = "2"
    new_pod.metadata.name = "apod"
    new_pod.metadata.namespace = "default"

    v1.read_namespaced_pod.side_effect = [
        pod, new_pod
    ]

    drain_nodes(name="mynode")

    v1.create_namespaced_pod_eviction.assert_called_with(
        "apod", "default", body=ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_daemonsets_cannot_be_drained(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    owner = MagicMock()
    owner.controller = True
    owner.kind = "DaemonSet"

    pod = MagicMock()
    pod.metadata.uid = "1"
    pod.metadata.name = "apod"
    pod.metadata.namespace = "default"
    pod.metadata.owner_references = [owner]

    pods = MagicMock()
    pods.items = [pod]
    v1.list_pod_for_all_namespaces.return_value = pods

    drain_nodes(name="mynode")

    v1.read_namespaced_pod.assert_not_called()
    v1.create_namespaced_pod_eviction.assert_not_called()


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_pod_with_local_volume_cannot_be_drained(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    owner = MagicMock()
    owner.controller = True
    owner.kind = "ReplicationSet"

    pod = MagicMock()
    pod.metadata.uid = "1"
    pod.metadata.name = "apod"
    pod.metadata.namespace = "default"
    pod.metadata.owner_references = [owner]
    volume = MagicMock()
    volume.empty_dir = True
    pod.spec.volumes = [volume]

    pods = MagicMock()
    pods.items = [pod]
    v1.list_pod_for_all_namespaces.return_value = pods

    drain_nodes(name="mynode")

    v1.read_namespaced_pod.assert_not_called()
    v1.create_namespaced_pod_eviction.assert_not_called()


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_pod_with_local_volume_cannot_be_drained_unless_forced(cl, client,
                                                               has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    owner = MagicMock()
    owner.controller = True
    owner.kind = "ReplicationSet"

    pod = MagicMock()
    pod.metadata.uid = "1"
    pod.metadata.name = "apod"
    pod.metadata.namespace = "default"
    pod.metadata.owner_references = [owner]

    pods = MagicMock()
    pods.items = [pod]
    v1.list_pod_for_all_namespaces.return_value = pods

    new_pod = MagicMock()
    new_pod.metadata.uid = "2"
    new_pod.metadata.name = "apod"
    new_pod.metadata.namespace = "default"

    v1.read_namespaced_pod.side_effect = [
        pod, new_pod
    ]

    drain_nodes(name="mynode", delete_pods_with_local_storage=True)

    v1.create_namespaced_pod_eviction.assert_called_with(
        "apod", "default", body=ANY)


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.node.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_mirror_pod_cannot_be_drained(cl, client, has_conf):
    has_conf.return_value = False

    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    node = MagicMock()
    node.metadata.name = "mynode"

    result = MagicMock()
    result.items = [node]
    v1.list_node.return_value = result

    owner = MagicMock()
    owner.controller = True
    owner.kind = "ReplicationSet"

    pod = MagicMock()
    pod.metadata.uid = "1"
    pod.metadata.name = "apod"
    pod.metadata.namespace = "default"
    pod.metadata.owner_references = [owner]
    pod.metadata.annotations = {
        "kubernetes.io/config.mirror": "..."
    }

    pods = MagicMock()
    pods.items = [pod]
    v1.list_pod_for_all_namespaces.return_value = pods

    drain_nodes(name="mynode")

    v1.read_namespaced_pod.assert_not_called()
    v1.create_namespaced_pod_eviction.assert_not_called()
