# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-kubernetes/compare/0.4.1...HEAD

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