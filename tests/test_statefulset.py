# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from chaosk8s.statefulset.actions import scale_statefulset


@patch('chaosk8s.has_local_config_file', autospec=True)
@patch('chaosk8s.statefulset.actions.client', autospec=True)
@patch('chaosk8s.client')
def test_scale_statefulset(cl, client, has_conf):
    has_conf.return_value = False

    body = {"spec": {"replicas": 0}}

    v1 = MagicMock()
    client.AppsV1Api.return_value = v1

    scale_statefulset(name="my-statefulset", replicas=0)

    assert v1.patch_namespaced_stateful_set.call_count == 1
    v1.patch_namespaced_stateful_set.assert_called_with(
        "my-statefulset", namespace="default", body=body)

