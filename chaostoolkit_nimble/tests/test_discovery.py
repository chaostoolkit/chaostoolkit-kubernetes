# -*- coding: utf-8 -*-

from chaostoolkit_nimble.core.extensions import __version__, discover


def test_discover_extension_capabilities():
    discovery = discover(discover_system=False)
    assert discovery["extension"]["name"] == "chaostoolkit-kubernetes"
    assert discovery["extension"]["version"] == __version__
    assert len(discovery["activities"]) > 0
