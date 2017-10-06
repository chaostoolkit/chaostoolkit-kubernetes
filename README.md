# Chaos Toolkit Kubernetes Support

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

First, in your experimenty project, make sure

To use the probes and actions from this package, add the following to your
experiment file:

```json
{
    "title": "Our microservice should really be gone by now",
    "layer": "kubernetes",
    "type": "python",
    "module": "chaosk8s.probes",
    "func": "microservice_available_and_healthy",
    "arguments": {
        "name": "mysvc"
    }
}
```

That's it!

Please explore the code to see existing provbes and actions.

## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please, fork this project, make your changes following the
usual [PEP 8][pep8] code style, sprinkling with tests and submit a PR for
review.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/
