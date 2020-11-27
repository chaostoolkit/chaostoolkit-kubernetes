# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.25.0...HEAD

## [0.25.0][] - 2020-11-23

[0.25.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.24.1...0.25.0

### Added

- Networking package with actions to add/remove network policies

### Changed

- Fix `actions.scale_deployment` to use AppsV1Api in line with the rest of the actions.

## [0.24.1][] - 2020-10-29

[0.24.1]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.24.0...0.24.1

### Changed

- `service_is_initialized` can no use a name, a label_selector or both
  to find a matching service in a namespace. The name is not matched against
  labels anymore but againt field selectors. [#106][106]
- declare return type of `service_is_initialized`

[106]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/issues/106

## [0.24.0][] - 2020-10-13

[0.24.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.23.0...0.24.0

### Changed

- Moved to stable API channel for deployment calls [#103][103] as they beta
  channels have been [deprecated][oldapi] for a while now.

[103]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/103
[oldapi]: https://cloud.google.com/kubernetes-engine/docs/release-notes#deprecated-apis-1-16

## [0.23.0][] - 2020-09-26

[0.23.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.22.0...0.23.0

### Added

- Add namespace to all probes and actions with backward compatibility [#39][39]  
- Added `statefulset_is_fully_available` and `statefulset_is_not_fully_available` [#86][86].
- Add custom resource objects actions and probes

[39]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/issues/39
[86]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/86

### Changed

- Fix `deployment_is_not_fully_available` and `deployment_is_fully_available` to use
  `metadata.name` field as a name selector as newer version of K8s no longer add a
  name label by default [#85][85].
- Fix `deployment_is_not_fully_available` and `deployment_is_fully_available` to only
  use `label_selector` if one is passed in [#85][85].

[85]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/85

## [0.22.0][] - 2020-01-10

[0.22.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.21.0...0.22.0

### Added

- Added function to execute remote commands in a container
- Added action to scale statefulsets [#73][73]
- Added action to create a statefulset from a json/yaml file [#74][74]
- Added action to create a service endpoint from a json/yaml file [#68][68]

### Changed

- Fix `microservice_available_and_healthy` to use `metadata.name` field as a name selector
  as newever version of K8s no longer add a name label by defult [#53][53].
- Fix `microservice_available_and_healthy` to only use `label_selector` if one is passed in [#53][53].
- Updates to `kubectl` api version to point to `apps/v1` instead of `apps/v1beta1`  [#65][65]
- Remove check Kubernetes statefulset by name and label  [#70][70]
- Fix yaml load warning #75

[53]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/53
[65]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/65
[68]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/68
[70]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/70
[73]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/73
[74]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/74
[75]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/75

## [0.21.0][] - 2019-09-02

[0.21.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.20.0...0.21.0

### Changed

- Try to read proxy from environment variable "HTTP_PROXY" and set it
  appropriately if it exists
- Add the `deployment_is_fully_available` probe to wait for a deployment to be fully available [#38][38]
- Fix calls to `delete_namespaced_*` so that the `body` argument is passed
  a named argument [#42][42]. A follow up to [#34][34]
- Fix calls to `delete_nodes` so that the `body` argument is passed
  a named argument [#44][44].

[38]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/38
[42]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/issues/42
[44]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/44

## [0.20.0][] - 2018-03-25

[0.20.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.19.1...0.20.0

### Added

- Add a probe to check pods conditions [PR#31][31]

[31]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/31

### Changed

- Fix call to `delete_namespaced_pod` so that the `body` argument is passed
  a named argument [#34][34]

[34]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/issues/34


## [0.19.1][] - 2018-10-08

[0.19.1]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.18.1...0.19.1

### Changed

-  As part of [#21][21], we realized that passing `None` to some parameters of the
   Kubernetes client API was not the right move because, in that case, the client
   turns that into a `"None"` string which is not what we want. So I had to
   resort to many conditionals that make the code not as clean I'd want. Sigh!

[21]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/issues/21

## [0.18.1][] - 2018-10-08

[0.18.1]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.18.0...0.18.1

### Changed

-  Fix: use `Succeeded` instead of `Completed` to filter successful pods created by a cronjob in the `all_microservices_healthy` probe.

## [0.18.0][] - 2018-10-08

[0.18.0]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.17.0...0.18.0

### Added

-  [Codecov][codecov] integration
-  Renamed `FailedActivity` to `ActivityFailed` as per [chaostoolkit 0.20.0][0.20.0]. See [PR#20][20]
-  Add Ability to specify a maximum percentage of pods to be killed [PR#19][19]
-  Consider `Completed` pods as healthy in the `all_microservices_healthy` probe. See [PR#23][23]
-  Support a new `grace_period_seconds` parameter in the `terminate_pods` action. See [PR#24][24]

[codecov]: https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes
[0.20.0]: https://github.com/chaostoolkit/chaostoolkit-lib/blob/master/CHANGELOG.md#0200---2018-08-09
[20]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/20
[19]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/pull/19

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
