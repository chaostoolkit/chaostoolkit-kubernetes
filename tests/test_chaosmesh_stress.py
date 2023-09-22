import json
from unittest.mock import ANY, MagicMock, patch

from chaosk8s.chaosmesh.stress.actions import stress_cpu, stress_memory


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_stress_cpu(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "StressChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = stress_cpu(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        workers=1,
        load=50,
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "stresschaos",
        ANY,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_stress_memory(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "chaos-mesh.org/v1alpha1", "kind": "StressChaos"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = stress_memory(
        "hello",
        ns="other",
        namespaces_selectors="default,other",
        label_selectors="a=b,c=d",
        annotations_selectors="h=5,u=8",
        workers=1,
        size="25%",
        container_names="a,b",
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "chaos-mesh.org",
        "v1alpha1",
        "other",
        "stresschaos",
        ANY,
        _preload_content=False,
    )
