# Chaos Toolkit Kubernetes Support

[![Build Status](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes.svg?branch=master)](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes)

This project contains activities, such as probes and actions, you can call from
your experiment through the Chaos Toolkit.

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
    "name": "all-our-microservices-should-be-healthy",
    "provider": {
        "type": "python",
        "module": "chaosk8s.probes",
        "func": "microservice_available_and_healthy",
        "arguments": {
            "name": "myapp",
            "ns": "myns"
        }
    }
}
```

That's it!

Please explore the code to see existing probes and actions.

### Discovery

You may use the Chaos Toolkit to discover the capabilities of this extension:

```
$ chaos discover chaostoolkit-kubernetes --no-install
```

## Configuration

This extension to the Chaos Toolkit can use the Kubernetes configuration 
found at the usual place in your HOME directory under `~/.kube/`. You can
also pass the credentials via secrets as follows:

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_HOST": "http://somehost",
            "KUBERNETES_API_KEY": {
                "type": "env",
                "key": "SO%E_ENV_VAR"
            }
        }
    }
}
```

Then in your probe or action:

```
{
    "name": "all-our-microservices-should-be-healthy",
    "provider": {
        "type": "python",
        "module": "chaosk8s.probes",
        "func": "microservice_available_and_healthy",
        "secrets": ["kubernetes"],
        "arguments": {
            "name": "myapp",
            "ns": "myns"
        }
    }
}
```

## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please fork this project, make your changes following the
usual [PEP 8][pep8] code style, add appropriate tests and submit a PR for
review.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/
