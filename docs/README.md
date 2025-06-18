# factorio: A fixtures replacement tool

[![build][build_badge]][build_url]
[![lint][lint_badge]][lint_url]
[![tests][tests_badge]][tests_url]
[![license][licence_badge]][licence_url]
[![codecov][codecov_badge]][codecov_url]
[![readthedocs][readthedocs_badge]][readthedocs_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]
[![build automation: yam][yam_badge]][yam_url]
[![Lint: ruff][ruff_badge]][ruff_url]

`factorio` is a fixtures replacement tool that's been heavily influenced by
[factory boy][factory_boy]. It's intention is to hide irrelevant fields when
writing a test.

Even though it's been designed to play well with various ORMs, it tries to
avoid any interaction with a database, as the saving/retrieving an object
shouldn't be the responsibility of the factory.

Under the hood it uses [faker] to create realistic values for each field.

## Links

- [Documentation]
- [Changelog]

[build_badge]: https://github.com/spapanik/factorio/actions/workflows/build.yml/badge.svg
[build_url]: https://github.com/spapanik/factorio/actions/workflows/build.yml
[lint_badge]: https://github.com/spapanik/factorio/actions/workflows/lint.yml/badge.svg
[lint_url]: https://github.com/spapanik/factorio/actions/workflows/lint.yml
[tests_badge]: https://github.com/spapanik/factorio/actions/workflows/tests.yml/badge.svg
[tests_url]: https://github.com/spapanik/factorio/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/factorio
[licence_url]: https://factorio.readthedocs.io/en/stable/LICENSE/
[codecov_badge]: https://codecov.io/github/spapanik/factorio/graph/badge.svg?token=Q20F84BW72
[codecov_url]: https://codecov.io/github/spapanik/factorio
[readthedocs_badge]: https://readthedocs.org/projects/factorio/badge/?version=latest
[readthedocs_url]: https://factorio.readthedocs.io/en/latest/
[pypi_badge]: https://img.shields.io/pypi/v/factorio
[pypi_url]: https://pypi.org/project/factorio
[pepy_badge]: https://pepy.tech/badge/factorio
[pepy_url]: https://pepy.tech/project/factorio
[yam_badge]: https://img.shields.io/badge/build%20automation-yamk-success
[yam_url]: https://github.com/spapanik/yamk
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff
[Documentation]: https://factorio.readthedocs.io/en/stable/
[Changelog]: https://factorio.readthedocs.io/en/stable/CHANGELOG/
[factory_boy]: https://github.com/FactoryBoy/factory_boy
[faker]: https://github.com/joke2k/faker
