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

## Quick Start

```python
from dataclasses import dataclass
from factorio import fields
from factorio.factories import Factory

@dataclass
class User:
    name: str
    email: str
    age: int

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=18, max_value=65)

user = UserFactory.build()
# user.name might be "Sarah Johnson"
# user.email might be "sarah.johnson@example.com"
# user.age might be 34
```

## Key Features

- **🎯 Explicit Object Creation**: Requires `.build()` method for clarity and safety
- **🚫 No Database Interaction**: Factories generate data, tests handle persistence
- **✨ Realistic Data**: Powered by Faker for lifelike test data
- **🔧 20+ Field Types**: From primitives to collections and nested factories
- **🎨 Flexible Overrides**: Override fields with values or dynamic field instances
- **📦 ORM Agnostic**: Works with dataclasses, Pydantic, SQLAlchemy, and more
- **🛡️ Type Safe**: Full type hints and mypy support

## Documentation

- **[Installation Guide](installation.md)** - Get started with factorio
- **[Usage Guide](usage.md)** - Basic to advanced usage patterns
- **[Field Reference](api/fields.md)** - Complete API reference for all field types
- **[Factory API](api/factory.md)** - Factory class documentation
- **[Integration Guides](integrations/)** - SQLAlchemy, Pydantic, and dataclasses
- **[Cookbook](cookbook.md)** - Common patterns and recipes
- **[Advanced Guide](guides/advanced.md)** - Advanced techniques and optimizations
- **[Changelog](CHANGELOG.md)** - Version history and changes

## Links

- [Full Documentation](https://factorio.readthedocs.io/en/stable/)
- [Changelog](CHANGELOG.md)
- [GitHub Repository](https://github.com/spapanik/factorio)
- [PyPI Package](https://pypi.org/project/factorio)

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
