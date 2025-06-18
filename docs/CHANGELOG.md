# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Fixed

- Fixed typing info for BooleanField

### Removed

- Dropped support factories with a Fields class

## [0.6.1] - 2024-11-25

### Fixed

- Fixed the StrEnum issues for py3.9/py3.10

## [0.6.0] - 2024-11-22

### Changed

- The Fields class is no longer needed (deprecated to be removed in 0.7.0)

## [0.5.0] - 2024-11-03

### Changed

- Changed license to BSD 3-Clause
- Changed the default limits for a collection field
- Model is now found from type hints
- Fields are now specific to each class

## [0.4.1] - 2024-01-24

### Fixed

- Relaxed the faker requirements

## [0.4.0] - 2023-10-28

### Added

- Added the ability to override a field that's not defined in fields

## [0.3.0] - 2023-07-14

### Changed

- Moved fields out of the Meta class, and into a separate Fields class

## [0.2.0] - 2023-06-08

### Added

- Added a choice field

### Removed

- Dropped python 3.7 support

## [0.1.0] - 2023-02-24

### Added

- Added a simple field, a collection field and a factory field

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[Unreleased]: https://github.com/spapanik/factorio/compare/v0.6.1...main
[0.6.1]: https://github.com/spapanik/factorio/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/spapanik/factorio/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/spapanik/factorio/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/spapanik/factorio/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/spapanik/factorio/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/spapanik/factorio/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/spapanik/factorio/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/spapanik/factorio/releases/tag/v0.1.0
