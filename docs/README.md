# factorio: A fixtures replacement tool

[![tests][test_badge]][test_url]
[![license][licence_badge]][licence_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]
[![code style: black][black_badge]][black_url]
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

-   [Documentation]
-   [Changelog]

[test_badge]: https://github.com/spapanik/factorio/actions/workflows/tests.yml/badge.svg
[test_url]: https://github.com/spapanik/factorio/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/factorio
[licence_url]: https://github.com/spapanik/factorio/blob/main/docs/LICENSE.md
[pypi_badge]: https://img.shields.io/pypi/v/factorio
[pypi_url]: https://pypi.org/project/factorio
[pepy_badge]: https://pepy.tech/badge/factorio
[pepy_url]: https://pepy.tech/project/factorio
[black_badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black_url]: https://github.com/psf/black
[yam_badge]: https://img.shields.io/badge/build%20automation-yamk-success
[yam_url]: https://github.com/spapanik/yamk
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff
[Documentation]: https://factorio.readthedocs.io/en/stable/
[Changelog]: https://github.com/spapanik/factorio/blob/main/docs/CHANGELOG.md
[factory_boy]: https://github.com/FactoryBoy/factory_boy
[faker]: https://github.com/joke2k/faker
