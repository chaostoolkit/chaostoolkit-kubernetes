#!/bin/bash
set -eo pipefail

function lint () {
    echo "Checking the code syntax"
    pycodestyle --first chaosk8s
}

function build () {
    echo "Building the choastoolkit package"
    python setup.py build
}

function run-test () {
    echo "Running the tests"
    python setup.py test
}

function release () {
    echo "Releasing the pachaage"
    python setup.py release

    echo "Publishing to PyPI"
    pip install twine
    twine upload dist/* -u ${PYPI_USER_NAME} -p ${PYPI_PWD}

    echo "Creating a new binary bundle of the toolkit and all known drivers/plugins"
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -H "Travis-API-Version: 3" \
        -H "Authorization: token "$TRAVIS_CI_TOKEN"" \
        -d '{"request": {"branch":"master", "message": "Rebuilding after new chaostoolkit-kubernetes release"}}' \
        https://api.travis-ci.org/repo/chaostoolkit%2Fchaostoolkit-bundler/requests
}

function main () {
    lint || return 1
    build || return 1
    run-test || return 1

    if [[ $TRAVIS_PYTHON_VERSION =~ ^3\.5+$ ]]; then
        if [[ $TRAVIS_TAG =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "Releasing tag $TRAVIS_TAG with Python $TRAVIS_PYTHON_VERSION"
            release || return 1
        fi
    fi
}

main "$@" || exit 1
exit 0
