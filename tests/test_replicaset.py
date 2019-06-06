# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock, ANY, call

from kubernetes.client.models import V1ReplicaSetList, V1ReplicaSet, V1ObjectMeta

from chaosk8s.replicaset.actions import delete_replica_set


@patch('chaosk8s.replicaset.actions.create_k8s_api_client', autospec=True)
@patch('chaosk8s.replicaset.actions.client', autospec=True)
def test_create_deployment(client, api):
    v1 = MagicMock()
    client.ExtensionsV1beta1Api.return_value = v1
    v1.list_namespaced_replica_set.return_value = V1ReplicaSetList(items=(
        V1ReplicaSet(metadata=V1ObjectMeta(name="repl1")),
        V1ReplicaSet(metadata=V1ObjectMeta(name="repl2"))
    ))

    delete_replica_set("fake", "fake_ns")

    v1.list_namespaced_replica_set.assert_called_with("fake_ns", label_selector="name in (fake)")
    v1.delete_namespaced_replica_set.assert_has_calls(
        [
            call("repl1", "fake_ns", ANY),
            call("repl2", "fake_ns", ANY)
        ],
        any_order=True
    )
