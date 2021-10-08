import os
from unittest.mock import MagicMock, patch

from chaosk8s import create_k8s_api_client


@patch("chaosk8s.has_local_config_file", autospec=True)
def test_client_can_be_created_from_environ(has_conf):
    has_conf.return_value = False
    os.environ.update(
        {
            "KUBERNETES_HOST": "http://someplace",
            "KUBERNETES_API_KEY": "6789",
            "KUBERNETES_API_KEY_PREFIX": "Boom",
        }
    )
    api = create_k8s_api_client()
    assert api.configuration.host == "http://someplace"
    assert api.configuration.api_key.get("authorization", "6789")
    assert api.configuration.api_key_prefix.get("authorization", "Boom")


@patch("chaosk8s.has_local_config_file", autospec=True)
def test_client_can_be_created_from_secrets(has_conf):
    has_conf.return_value = False
    secrets = {
        "KUBERNETES_HOST": "http://someplace",
        "KUBERNETES_API_KEY": "6789",
        "KUBERNETES_API_KEY_PREFIX": "Boom",
    }
    api = create_k8s_api_client(secrets)
    assert api.configuration.host == "http://someplace"
    assert api.configuration.api_key.get("authorization", "6789")
    assert api.configuration.api_key_prefix.get("authorization", "Boom")


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.config.load_incluster_config", autospec=True)
@patch.dict(os.environ, {"CHAOSTOOLKIT_IN_POD": "true"})
def test_client_can_be_created_when_ctk_in_prod(load_incluster_config, has_conf):
    has_conf.return_value = False
    load_incluster_config.return_value = None
    _ = create_k8s_api_client()
    load_incluster_config.assert_called_once_with()


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.config", autospec=True)
@patch.dict(os.environ, {"KUBERNETES_CONTEXT": "minikube"})
def test_client_can_provide_a_context(cfg, has_conf):
    has_conf.return_value = True
    cfg.load_kube_config = MagicMock()
    _ = create_k8s_api_client()
    cfg.load_kube_config.assert_called_with(context="minikube")
