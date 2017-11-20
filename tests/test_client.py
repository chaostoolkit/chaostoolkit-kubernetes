# -*- coding: utf-8 -*-
import os
from unittest.mock import MagicMock, patch

from kubernetes import client, config
import pytest

from chaosk8s import create_k8s_api_client


@patch('chaosk8s.has_local_config_file', autospec=True)
def test_client_can_be_created_from_environ(has_conf):
    has_conf.return_value = False
    os.environ.update({
        "KUBERNETES_HOST": "http://someplace",
        "KUBERNETES_API_KEY": "6789",
        "KUBERNETES_API_KEY_PREFIX": "Boom"
    })
    api = create_k8s_api_client()
    assert api.configuration.host == "http://someplace"
    assert api.configuration.api_key.get("authorization", "6789")
    assert api.configuration.api_key_prefix.get("authorization", "Boom")


@patch('chaosk8s.has_local_config_file', autospec=True)
def test_client_can_be_created_from_secrets(has_conf):
    has_conf.return_value = False
    secrets = {
        "KUBERNETES_HOST": "http://someplace",
        "KUBERNETES_API_KEY": "6789",
        "KUBERNETES_API_KEY_PREFIX": "Boom"
    }
    api = create_k8s_api_client(secrets)
    assert api.configuration.host == "http://someplace"
    assert api.configuration.api_key.get("authorization", "6789")
    assert api.configuration.api_key_prefix.get("authorization", "Boom")