# Installation

## Quick Install

### Using uv (Recommended)

[uv] is an extremely fast Python package installer. You can use it to install `factorio` and try it out:

```console
$ uv pip install factorio
```

### Using pip

```console
$ pip install factorio
```

### Using Poetry

```console
$ poetry add factorio
```

## Project Configuration

### Using a PEP 621 compliant build backend

[PEP 621] is the standard way to store your dependencies in a `pyproject.toml` file. You can add `factorio` to your `pyproject.toml` file:

```toml
[project]
dependencies = [
    "factorio~=0.7",
]
```

### Using requirements.txt

```text
factorio~=0.7
```

## Python Version Requirement

⚠️ **Important**: `factorio` requires **Python 3.10 or higher**.

If you're not using uv, please ensure that you have a compatible Python version installed on your system.

Check your Python version:
```console
$ python --version
Python 3.10.0
```

## Dependencies

factorio depends on:
- **[faker](https://github.com/joke2k/faker)** >= 30.8 - For realistic data generation
- **[pyutilkit](https://pypi.org/project/pyutilkit/)** ~= 0.11 - Utility functions
- **tzdata** (Windows only) - Timezone data

These dependencies are automatically installed when you install factorio.

## Verification

After installation, verify that factorio is working:

```python
python -c "from factorio.factories import Factory; print('factorio installed successfully!')"
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're using Python 3.10+:

```console
$ python3.10 -m pip install factorio
```

### Version Conflicts

If you encounter version conflicts with faker or other dependencies:

```console
$ uv pip install factorio --upgrade
```

Or with pip:

```console
$ pip install factorio --upgrade
```

### Virtual Environments

It's recommended to use virtual environments:

```console
# Create virtual environment
$ python -m venv .venv

# Activate it
$ source .venv/bin/activate  # Linux/Mac
$ .venv\Scripts\activate     # Windows

# Install factorio
$ pip install factorio
```

## Next Steps

- Read the [Quick Start Guide](usage.md) to learn how to use factorio
- Check out the [Field Reference](api/fields.md) for all available field types
- Browse the [Cookbook](cookbook.md) for common patterns

[uv]: https://github.com/astral-sh/uv
[PEP 621]: https://peps.python.org/pep-0621/
