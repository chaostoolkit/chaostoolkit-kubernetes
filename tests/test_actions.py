# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from chaoslib.exceptions import FailedProbe
from kubernetes import client, config
import pytest

from chaosk8s.actions import start_microservice, kill_microservice


@patch('chaosk8s.has_local_config_file', autospec=True)
def test_cannot_process_other_than_yaml_and_json(has_conf):
    has_conf.return_value = False
    path = "./tests/fixtures/invalid-k8s.txt"
    with pytest.raises(FailedProbe) as excinfo:
        start_microservice(spec_path=path)
    assert "cannot process {path}".format(path=path) in str(excinfo)
