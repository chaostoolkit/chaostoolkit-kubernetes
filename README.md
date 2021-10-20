# Chaos Toolkit Extensions for Kubernetes

[![Build Status](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes.svg?branch=master)](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes)
[![codecov](https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes/branch/master/graph/badge.svg)](https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-kubernetes.svg)](https://www.python.org/)
[![Downloads](https://pepy.tech/badge/chaostoolkit-kubernetes)](https://pepy.tech/project/chaostoolkit-kubernetes)

This project contains activities, such as probes and actions, you can call from
your experiment through the Chaos Toolkit to perform Chaos Engineering against
the Kubernetes API: killing a pod, removing a statefulset or node...

## Install

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.

[chaostoolkit]: https://github.com/chaostoolkit/chaostoolkit

```
$ pip install chaostoolkit-kubernetes
```

## Usage

To use the probes and actions from this package, add the following to your
experiment file:

```json
{
    "title": "Do we remain available in face of pod going down?",
    "description": "We expect Kubernetes to handle the situation gracefully when a pod goes down",
    "tags": ["kubernetes"],
    "steady-state-hypothesis": {
        "title": "Verifying service remains healthy",
        "probes": [
            {
                "name": "all-our-microservices-should-be-healthy",
                "type": "probe",
                "tolerance": true,
                "provider": {
                    "type": "python",
                    "module": "chaosk8s.probes",
                    "func": "microservice_available_and_healthy",
                    "arguments": {
                        "name": "myapp"
                    }
                }
            }
        ]
    },
    "method": [
        {
            "type": "action",
            "name": "terminate-db-pod",
            "provider": {
                "type": "python",
                "module": "chaosk8s.pod.actions",
                "func": "terminate_pods",
                "arguments": {
                    "label_selector": "app=my-app",
                    "name_pattern": "my-app-[0-9]$",
                    "rand": true
                }
            },
            "pauses": {
                "after": 5
            }
        }
    ]
}
```

That's it! Notice how the action gives you the way to kill one pod randomly.

Please explore the [documentation][doc] to see existing probes and actions.

[doc]: https://docs.chaostoolkit.org/drivers/kubernetes/#exported-activities

## Configuration

### Use ~/.kube/config

If you have a valid entry in your `~/.kube/config` file for the cluster you
want to target, then there is nothing to be done.

You may specify `KUBECONFIG` to specify a different location.

```
$ export KUBECONFIG=/tmp/my-config
```

#### Specify the Kubernetes context

Quite often, your Kubernetes configuration contains several entries and you
need to define the one to use as a default context when not it isn't
explicitely provided.

You may of course change your default using
`kubectl config use-context KUBERNETES_CONTEXT` but you can also be explicit
in your experiment as follows:

```json
{
    "title": "Do we remain available in face of pod going down?",
    "description": "We expect Kubernetes to handle the situation gracefully when a pod goes down",
    "tags": ["kubernetes"],
    "secrets": {
        "k8s": {
            "KUBERNETES_CONTEXT": "..."
        }
    },
    "steady-state-hypothesis": {
        "title": "Verifying service remains healthy",
        "probes": [
            {
                "name": "all-our-microservices-should-be-healthy",
                "type": "probe",
                "tolerance": true,
                "secrets": ["k8s"],
                "provider": {
                    "type": "python",
                    "module": "chaosk8s.probes",
                    "func": "microservice_available_and_healthy",
                    "arguments": {
                        "name": "myapp"
                    }
                }
            }
        ]
    },
    "method": [
        {
            "type": "action",
            "name": "terminate-db-pod",
            "secrets": ["k8s"],
            "provider": {
                "type": "python",
                "module": "chaosk8s.pod.actions",
                "func": "terminate_pods",
                "arguments": {
                    "label_selector": "app=my-app",
                    "name_pattern": "my-app-[0-9]$",
                    "rand": true
                }
            },
            "pauses": {
                "after": 5
            }
        }
    ]
}
```

You need to specify the `KUBERNETES_CONTEXT` secret key to the name of the
context you want the experiment to use. Make sure to also inform the
actions and probes about the secret entries they should be
passed `"secrets": ["k8s"]`.

### Use a Pod's service account

When running from a pod (not your local machine or a CI for instance), the
 `./.kube/config` file does not exist. Instead, the credentials can be found
 at [/var/run/secrets/kubernetes.io/serviceaccount/token][podcreds].

 [podcreds]: https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/#accessing-the-api-from-a-pod

 To let the extension know about this, simply set `CHAOSTOOLKIT_IN_POD` from the
 environment variable of the pod specification:

```yaml
env:
- name: CHAOSTOOLKIT_IN_POD
  value: "true"
```

## Pass all credentials in the experiment

Finally, you may pass explicitely all required credentials information to the
experiment as follows:

### Using an API key

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_HOST": "http://somehost",
            "KUBERNETES_API_KEY": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            }
        }
    }
}
```

### Using a username/password

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_HOST": "http://somehost",
            "KUBERNETES_USERNAME": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            },
            "KUBERNETES_PASSWORD": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            }
        }
    }
}
```

### Using a TLS key/certificate

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_HOST": "http://somehost",
            "KUBERNETES_CERT_FILE": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            },
            "KUBERNETES_KEY_FILE": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            }
        }
    }
}
```

## Managed Kubernetes Clusters Authentication

On some managed Kubernetes clusters, you also need to authenticate against the
platform itself because the Kubernetes authentication is delegated to it.

### Google Cloud Platform

In addition to your Kubernetes credentials (via the `~/.kube/config` file), you
need to authenticate against the Google Cloud Platform itself. Usually this
is done [via][gcloud]:

[gcloud]: https://cloud.google.com/sdk/gcloud/reference/auth/login

```
$ gcloud auth login
```

But can also be achieved by defining the `GOOGLE_APPLICATION_CREDENTIALS`
environment variable.

## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please, fork this project, write unit tests to cover the proposed changes,
implement the changes, ensure they meet the formatting standards set out by `black`,
`flake8`, and `isort`, and then raise a PR to the repository for review.

Please refer to the [formatting](#formatting-and-linting) section for more information
on the formatting standards.

The Chaos Toolkit projects require all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR.

[dco]: https://github.com/probot/dco#how-it-works

### Develop

If you wish to develop on this project, make sure to install the development
dependencies. But first, [create a virtual environment][venv] and then install
those dependencies.

[venv]: http://chaostoolkit.org/reference/usage/install/#create-a-virtual-environment

```console
$ make install-dev
```

Now, you can edit the files and they will be automatically be seen by your
environment, even when running from the `chaos` command locally.

### Tests

To run the tests for the project execute the following:

```console
$ make tests
```

### Formatting and Linting

We use a combination of [`black`][black], [`flake8`][flake8], and [`isort`][isort] to both
lint and format this repositories code.

[black]: https://github.com/psf/black
[flake8]: https://github.com/PyCQA/flake8
[isort]: https://github.com/PyCQA/isort

Before raising a Pull Request, we recommend you run formatting against your code with:

```console
$ make format
```

This will automatically format any code that doesn't adhere to the formatting standards.

As some things are not picked up by the formatting, we also recommend you run:

```console
$ make lint
```

To ensure that any unused import statements/strings that are too long, etc. are also picked up.
```
