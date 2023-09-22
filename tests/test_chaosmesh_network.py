import json
from unittest.mock import ANY, MagicMock, patch

from chaosk8s.chaosmesh.network.actions import (
    add_latency,
    corrupt_packets,
    duplicate_packets,
    reorder_packets,
    set_bandwidth,
    set_loss,
)


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_add_latency(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "NetworkChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = add_latency(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        latency="200ms",
        jitter="1ms",
        correlation="50",
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "networkchaos",
        ANY,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_set_loss(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "NetworkChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = set_loss(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        loss="50",
        correlation="50",
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "networkchaos",
        ANY,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_duplicate_packets(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "NetworkChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = duplicate_packets(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        duplicate="50",
        correlation="50",
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "networkchaos",
        ANY,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_reorder_packets(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "NetworkChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = reorder_packets(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        reorder="0.5",
        gap="5",
        correlation="50",
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "networkchaos",
        ANY,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_corrupt_packets(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "NetworkChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = corrupt_packets(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        corrupt="5",
        correlation="50",
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "networkchaos",
        ANY,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_set_bandwidth(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "NetworkChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = set_bandwidth(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        rate="1mbps",
        limit=1,
        buffer=1,
        peakrate=1,
        minburst=1,
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "networkchaos",
        ANY,
        _preload_content=False,
    )
