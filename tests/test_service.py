# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock

from chaosk8s.service.actions import delete_service


@patch('chaosk8s.service.actions.create_k8s_api_client', autospec=True)
@patch('chaosk8s.service.actions.client', autospec=True)
def test_delete_service(client, api):
    v1 = MagicMock()
    client.CoreV1Api.return_value = v1

    delete_service("fake", "fake_ns")

    v1.delete_namespaced_service.assert_called_with("fake", namespace="fake_ns")
