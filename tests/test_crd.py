import json
from tempfile import NamedTemporaryFile
from unittest.mock import ANY, MagicMock, patch

import pytest
import yaml
from chaoslib.exceptions import ActivityFailed
from kubernetes.client.rest import ApiException

from chaosk8s.crd.actions import (
    apply_from_json,
    apply_from_yaml,
    create_cluster_custom_object,
    create_custom_object,
    delete_custom_object,
    patch_custom_object,
    replace_custom_object,
)
from chaosk8s.crd.probes import get_custom_object, list_custom_objects


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_cro(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "stable.example.com/v1", "kind": "CronTab"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)
    resource = {
        "group": "stable.example.com",
        "version": "v1",
        "plural": "crontabs",
        "resource": {
            "apiVersion": "stable.example.com/v1",
            "kind": "CronTab",
            "metadata": {"name": "my-new-cron-object"},
            "spec": {"cronSpec": "* * * * */5", "image": "my-awesome-cron-image"},
        },
    }

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = create_custom_object(
        group="stable.example.com", version="v1", plural="crontabs", resource=resource
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        resource,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_cro_from_file(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "stable.example.com/v1", "kind": "CronTab"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    with NamedTemporaryFile() as f:
        f.write(
            json.dumps(
                {
                    "apiVersion": "stable.example.com/v1",
                    "kind": "CronTab",
                    "metadata": {"name": "my-new-cron-object"},
                    "spec": {
                        "cronSpec": "* * * * */5",
                        "image": "my-awesome-cron-image",
                    },
                }
            ).encode("utf-8")
        )
        f.seek(0)

        resource = {
            "group": "stable.example.com",
            "version": "v1",
            "plural": "crontabs",
            "resource_as_yaml_file": f.name,
        }

        v1 = MagicMock()
        client.CustomObjectsApi.return_value = v1
        v1.create_namespaced_custom_object.return_value = resp

        o = create_custom_object(
            group="stable.example.com",
            version="v1",
            plural="crontabs",
            resource=resource,
        )
        assert o == resp_data

        assert v1.create_namespaced_custom_object.call_count == 1
        v1.create_namespaced_custom_object.assert_called_with(
            "stable.example.com",
            "v1",
            "default",
            "crontabs",
            ANY,
            _preload_content=False,
        )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_cluster_cro(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "stable.example.com/v1", "kind": "CronTab"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)
    resource = {
        "group": "stable.example.com",
        "version": "v1",
        "plural": "crontabs",
        "resource": {
            "apiVersion": "stable.example.com/v1",
            "kind": "CronTab",
            "metadata": {"name": "my-new-cron-object"},
            "spec": {"cronSpec": "* * * * */5", "image": "my-awesome-cron-image"},
        },
    }

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_cluster_custom_object.return_value = resp

    o = create_cluster_custom_object(
        group="stable.example.com", version="v1", plural="crontabs", resource=resource
    )
    assert o == resp_data

    assert v1.create_cluster_custom_object.call_count == 1
    v1.create_cluster_custom_object.assert_called_with(
        "stable.example.com", "v1", "crontabs", resource, _preload_content=False
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_cluster_cro_from_file(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "stable.example.com/v1", "kind": "CronTab"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    with NamedTemporaryFile() as f:
        f.write(
            json.dumps(
                {
                    "apiVersion": "stable.example.com/v1",
                    "kind": "CronTab",
                    "metadata": {"name": "my-new-cron-object"},
                    "spec": {
                        "cronSpec": "* * * * */5",
                        "image": "my-awesome-cron-image",
                    },
                }
            ).encode("utf-8")
        )
        f.seek(0)

        resource = {
            "group": "stable.example.com",
            "version": "v1",
            "plural": "crontabs",
            "resource_as_yaml_file": f.name,
        }

        v1 = MagicMock()
        client.CustomObjectsApi.return_value = v1
        v1.create_cluster_custom_object.return_value = resp

        o = create_cluster_custom_object(
            group="stable.example.com",
            version="v1",
            plural="crontabs",
            resource=resource,
        )
        assert o == resp_data

        assert v1.create_cluster_custom_object.call_count == 1
        v1.create_cluster_custom_object.assert_called_with(
            "stable.example.com", "v1", "crontabs", ANY, _preload_content=False
        )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_cro_allows_conflicts(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {
        "kind": "Status",
        "apiVersion": "v1",
        "metadata": {},
        "status": "Failure",
        "message": 'crontabs.stable.example.com "my-new-cron-object" already exists',
        "reason": "AlreadyExists",
        "details": {
            "name": "my-new-cron-object",
            "group": "stable.example.com",
            "kind": "crontabs",
        },
        "code": 409,
    }

    resp = MagicMock()
    resp.status = 409
    resp.reason = "Conflicts"
    resp.data = json.dumps(resp_data)
    resource = {
        "group": "stable.example.com",
        "version": "v1",
        "plural": "crontabs",
        "resource": {
            "apiVersion": "stable.example.com/v1",
            "kind": "CronTab",
            "metadata": {"name": "my-new-cron-object"},
            "spec": {"cronSpec": "* * * * */5", "image": "my-awesome-cron-image"},
        },
    }

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.side_effect = ApiException(http_resp=resp)

    o = create_custom_object(
        group="stable.example.com", version="v1", plural="crontabs", resource=resource
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        resource,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_creating_cro_allows_fails_whencrd_not_applied_first(cl, client, has_conf):
    has_conf.return_value = False

    resp = MagicMock()
    resp.status = 404
    resp.reason = "Not Found"
    resource = {
        "group": "stable.example.com",
        "version": "v1",
        "plural": "crontabs",
        "resource": {
            "apiVersion": "stable.example.com/v1",
            "kind": "CronTab",
            "metadata": {"name": "my-new-cron-object"},
            "spec": {"cronSpec": "* * * * */5", "image": "my-awesome-cron-image"},
        },
    }

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.side_effect = ApiException(http_resp=resp)

    with pytest.raises(ActivityFailed):
        create_custom_object(
            group="stable.example.com",
            version="v1",
            plural="crontabs",
            resource=resource,
        )

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        resource,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_deleting_cro(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {
        "apiVersion": "stable.example.com/v1",
        "kind": "CronTab",
        "status": "Success",
    }
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.delete_namespaced_custom_object.return_value = resp

    o = delete_custom_object(
        group="stable.example.com",
        version="v1",
        plural="crontabs",
        name="my-new-cron-object",
    )
    assert o == resp_data

    assert v1.delete_namespaced_custom_object.call_count == 1
    v1.delete_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        "my-new-cron-object",
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_patching_cro(cl, client, has_conf):
    has_conf.return_value = False

    resource = {}
    resp_data = {
        "apiVersion": "stable.example.com/v1",
        "kind": "CronTab",
        "status": "Success",
    }
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.patch_namespaced_custom_object.return_value = resp

    o = patch_custom_object(
        group="stable.example.com",
        version="v1",
        plural="crontabs",
        name="my-new-cron-object",
        resource=resource,
    )
    assert o == resp_data

    assert v1.patch_namespaced_custom_object.call_count == 1
    v1.patch_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        "my-new-cron-object",
        resource,
        force=False,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_replacing_cro(cl, client, has_conf):
    has_conf.return_value = False

    resource = {}
    resp_data = {
        "apiVersion": "stable.example.com/v1",
        "kind": "CronTab",
        "status": "Success",
    }
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.replace_namespaced_custom_object.return_value = resp

    o = replace_custom_object(
        group="stable.example.com",
        version="v1",
        plural="crontabs",
        name="my-new-cron-object",
        resource=resource,
    )
    assert o == resp_data

    assert v1.replace_namespaced_custom_object.call_count == 1
    v1.replace_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        "my-new-cron-object",
        resource,
        force=False,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_getting_a_cro(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "stable.example.com/v1", "kind": "CronTab"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.get_namespaced_custom_object.return_value = resp

    o = get_custom_object(
        group="stable.example.com",
        version="v1",
        plural="crontabs",
        name="my-new-cron-object",
    )
    assert o == resp_data

    assert v1.get_namespaced_custom_object.call_count == 1
    v1.get_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        "my-new-cron-object",
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.probes.client", autospec=True)
@patch("chaosk8s.client")
def test_listing_cros(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = [{"apiVersion": "stable.example.com/v1", "kind": "CronTab"}]
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.list_namespaced_custom_object.return_value = resp

    o = list_custom_objects(group="stable.example.com", version="v1", plural="crontabs")
    assert o == resp_data

    assert v1.list_namespaced_custom_object.call_count == 1
    v1.list_namespaced_custom_object.assert_called_with(
        "stable.example.com", "v1", "default", "crontabs", _preload_content=False
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_apply_from_json(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "stable.example.com/v1", "kind": "CronTab"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = apply_from_json(
        resource=json.dumps(
            {
                "apiVersion": "stable.example.com/v1",
                "kind": "CronTab",
                "metadata": {"name": "my-new-cron-object"},
                "spec": {
                    "cronSpec": "* * * * */5",
                    "image": "my-awesome-cron-image",
                },
            }
        )
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        ANY,
        _preload_content=False,
    )


@patch("chaosk8s.has_local_config_file", autospec=True)
@patch("chaosk8s.crd.actions.client", autospec=True)
@patch("chaosk8s.client")
def test_apply_from_yaml(cl, client, has_conf):
    has_conf.return_value = False

    resp_data = {"apiVersion": "stable.example.com/v1", "kind": "CronTab"}
    resp = MagicMock()
    resp.data = json.dumps(resp_data)

    v1 = MagicMock()
    client.CustomObjectsApi.return_value = v1
    v1.create_namespaced_custom_object.return_value = resp

    o = apply_from_yaml(
        resource=yaml.safe_dump(
            {
                "apiVersion": "stable.example.com/v1",
                "kind": "CronTab",
                "metadata": {"name": "my-new-cron-object"},
                "spec": {
                    "cronSpec": "* * * * */5",
                    "image": "my-awesome-cron-image",
                },
            }
        )
    )
    assert o == resp_data

    assert v1.create_namespaced_custom_object.call_count == 1
    v1.create_namespaced_custom_object.assert_called_with(
        "stable.example.com",
        "v1",
        "default",
        "crontabs",
        ANY,
        _preload_content=False,
    )
