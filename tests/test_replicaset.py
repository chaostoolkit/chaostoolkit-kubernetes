from unittest.mock import ANY, MagicMock, call, patch

from kubernetes.client.models import V1ObjectMeta, V1ReplicaSet, V1ReplicaSetList

from chaosk8s.replicaset.actions import delete_replica_set


@patch("chaosk8s.replicaset.actions.create_k8s_api_client", autospec=True)
@patch("chaosk8s.replicaset.actions.client", autospec=True)
def test_delete_replica_set(client, api):
    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    v1.list_namespaced_replica_set.return_value = V1ReplicaSetList(
        items=(
            V1ReplicaSet(metadata=V1ObjectMeta(name="repl1")),
            V1ReplicaSet(metadata=V1ObjectMeta(name="repl2")),
        )
    )

    delete_replica_set("fake", "fake_ns")

    v1.list_namespaced_replica_set.assert_called_with(
        "fake_ns", field_selector="metadata.name=fake"
    )
    v1.delete_namespaced_replica_set.assert_has_calls(
        [call("repl1", "fake_ns", body=ANY), call("repl2", "fake_ns", body=ANY)],
        any_order=True,
    )
