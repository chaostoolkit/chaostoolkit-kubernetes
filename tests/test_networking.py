# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from chaosk8s.networking.actions import create_network_policy


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.networking.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_create_network_policy_from_spec(cl, client, has_conf):
    has_conf.return_value = False

    spec = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {
            "name": "deny-all-ingress-to-foo"
        },
        "spec": {
            "podSelector": "app=foo",
            "policyTypes": [
                "Ingress"
            ],
            "ingress": []
        }
    }

    v1 = MagicMock()
    client.NetworkingV1Api.return_value = v1

    create_network_policy(spec=spec)

    assert v1.create_namespaced_network_policy.call_count == 1
    v1.create_namespaced_network_policy.assert_called_with(
        "default", body=spec)
