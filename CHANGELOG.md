# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.17.0...HEAD

### Added

-  [Codecov][codecov] integration

[codecov]: https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes

## [0.17.0][] - 2018-09-07

[0.17.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.16.2...0.17.0

### Added

-   List work nodes

## [0.16.2][] - 2018-05-14

[0.16.2]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.16.1...0.16.2

### Added

-   Read version from source file without importing

## [0.16.1][] - 2018-05-14

[0.16.1]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.16.0...0.16.1

### Added

-   Added requirements-dev.txt to MANIFEST.in so it gets packaged and distributed

## [0.16.0][] - 2018-04-24

[0.16.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.15.0...0.16.0

### Added

-   Allow to pass the Kubernetes context to authenticate from by setting
    the `"KUBERNETES_CONTEXT"` key in the environment or the secrets object
    [#15][15]

[15]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/issues/15

## [0.15.0][] - 2018-04-13

[0.15.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.14.0...0.15.0

### Added

-   a probe to count the number of pods
-   actions to delete and create nodes
-   actions to cordon, uncordon and drain nodes
-   canot locate credentials automatically when ran from within a Pod if
    you set the `CHAOSTOOLKIT_IN_POD: "true"` environment variable in the Pod
    spec

## [0.14.0][] - 2018-04-05

[0.14.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.13.0...0.14.0

### Added

-   allow to create a Kubernetes client from a Kubernetes cluster pod

## [0.13.0][] - 2018-03-09

[0.13.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.12.0...0.13.0

### Added

-   `chaosk8s.pod.probes.pods_in_phase` to probe that all pods matching a label
    are in a given pod Phase
-   `chaosk8s.pod.probes.pods_not_in_phase` to probe that all pods matching a
    label are not in a given pod Phase

## [0.12.0][] - 2018-02-12

[0.12.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.11.0...0.12.0

### Changed

-   Moved the `chaosk8s.probes.read_microservice_logs` to 
    `chaosk8s.pod.probes.read_pod_logs` for clarity
-   Make name optional for `chaosk8s.pod.probes.read_pod_logs` as it usually
    more preferred to use a label for that probe
-   Removed the system discovery as it wasn't used by chaostoolkit anyway

## [0.11.0][] - 2018-01-28

[0.11.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.10.0...0.11.0

### Added

-   Added a pod specific set of actions

### Changed

-   Refactor dev/test dependencies so they are not deployed on install

## [0.10.0][] - 2018-01-22

[0.10.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.9.0...0.10.0

### Changed

- activities now take a `label_selector` argument to let you adjust to your
  conventions when selecting resources [#7][7]

[7]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/issues/7

## [0.9.0][] - 2018-01-16

[0.9.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.8.0...0.9.0

### Added

- discovery mechanism

## [0.8.0][] - 2017-12-29

[0.8.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.7.0...0.8.0

### Added

- `read_microservices_logs` probe to fetch pod's logs

## [0.7.0][] - 2017-12-17

[0.7.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.6.0...0.7.0

### Added

- Deployment scaler action

### Changed

- Updated to chaostoolkit-lib 0.8.0

## [0.6.0][] - 2017-12-12

[0.6.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.5.0...0.6.0

### Added

- Logging at DEBUG level for investigation
- Probe `deployment_is_not_fully_available` to wait until a deployment is not
  fully available (its desired state is different from its current state)

### Changed

- Selecting on the name Label rather than Service as it's more commonly used
- Updated chaostoolkit-lib to 0.7.0 for configuration support

## [0.5.0][] - 2017-12-06

[0.5.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.4.3...0.5.0

### Changed

- Updated to match chaostoolkit-lib 0.6.0 API changes
- Probes now return `True` on success so they can be nicely used from the
  steady state hypothesis checks

## [0.4.3][] - 2017-11-23

[0.4.3]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.4.2...0.4.3

### Changed

- Removing unwanted parameter

## [0.4.2][] - 2017-11-20

[0.4.2]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.4.1...0.4.2

### Changed

- Proper verify SSL reading of the environment key

## [0.4.1][] - 2017-11-20

[0.4.1]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.4.0...0.4.1

### Added

- Passing secrets down to client function


## [0.4.0][] - 2017-11-20

[0.4.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.3.0...0.4.0

### Added

- Can create a client from secrets


## [0.3.0][] - 2017-11-20

[0.3.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.2.0...0.3.0

### Added

- Can now authenticate to the Kubernetes API endpoint either via a token,
  username/password or certificate/pkey. All of this via environment variable.
  By default, still looks up for ~/kube/config if it exists


## [0.2.0][] - 2017-10-23

[0.2.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.1.1...0.2.0

### Added

- Remove check Kubernetes service by name

### Changed

-   Do not build a universal wheel package (no Python 2 support in chaostoolkit)

## [0.1.1][] - 2017-10-06

[0.1.1]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.1.0...0.1.1

### Changed

-   Package up extra files when installed from source

## [0.1.0][] - 2017-10-06

[0.1.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/tree/0.1.0

### Added

-   Initial release