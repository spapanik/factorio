# Enums API Reference

factorio provides custom enum implementations to support string-based enumerations with enhanced functionality.

## StrEnum

A string-based enumeration that provides case-insensitive comparison and seamless string integration.

### Overview

`StrEnum` extends Python's `Enum` to behave like strings while maintaining enum benefits. Each member's value is automatically set to its name in lowercase.

**Inherits from:** `str`, `Enum`

### Features

#### Automatic Value Generation

Member values are automatically generated as lowercase versions of their names:

```python
from factorio.lib.enums import StrEnum
from enum import auto

class Color(StrEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

assert Color.RED == "red"
assert Color.GREEN == "green"
assert str(Color.BLUE) == "blue"
```

#### Case-Insensitive Comparison

Compare enum members with strings regardless of case:

```python
class Status(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()
    PENDING = auto()

assert Status.ACTIVE == "active"
assert Status.ACTIVE == "ACTIVE"
assert Status.ACTIVE == "Active"
assert Status.PENDING == "pending"
```

#### String Operations

Since `StrEnum` inherits from `str`, you can use all string methods:

```python
class Priority(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()

# String methods work
assert Priority.HIGH.upper() == "HIGH"
assert Priority.LOW.capitalize() == "Low"
assert Priority.MEDIUM.startswith("med")

# String formatting
message = f"Priority: {Priority.HIGH}"
assert message == "Priority: high"

# String concatenation
result = "status_" + Priority.ACTIVE
assert result == "status_active"
```

#### Hash Compatibility

Enum members hash the same as their string values:

```python
class Role(StrEnum):
    ADMIN = auto()
    USER = auto()
    GUEST = auto()

# Can be used in sets and dicts
role_set = {Role.ADMIN, Role.USER}
assert "admin" in role_set  # String lookup works

role_dict = {Role.ADMIN: "Administrator", Role.USER: "Regular User"}
assert role_dict["admin"] == "Administrator"  # String key works
```

### Methods

#### `__str__() -> str`

Returns the string value of the enum member.

```python
class Mode(StrEnum):
    DEBUG = auto()
    RELEASE = auto()

assert str(Mode.DEBUG) == "debug"
print(Mode.RELEASE)  # Prints: release
```

#### `__eq__(value: object) -> bool`

Compares the enum member with another value. Supports comparison with strings (case-insensitive).

**Parameters:**
- `value`: The value to compare against (str or StrEnum)

**Returns:** `True` if equal, `False` otherwise

```python
class State(StrEnum):
    ON = auto()
    OFF = auto()

assert State.ON == "on"
assert State.ON == "ON"
assert State.ON == State.ON
assert State.ON != State.OFF
assert State.ON != "off"
```

#### `__ne__(value: object) -> bool`

Negated equality comparison.

```python
assert State.ON != "off"
assert State.ON != State.OFF
```

#### `__hash__() -> int`

Returns the hash of the string value, making it compatible with string keys.

```python
assert hash(State.ON) == hash("on")

# Works in dictionaries
config = {State.ON: True, State.OFF: False}
assert config["on"] is True
```

### Use Cases

#### Configuration Keys

```python
class ConfigKey(StrEnum):
    DATABASE_URL = auto()
    API_KEY = auto()
    DEBUG_MODE = auto()

config = {
    ConfigKey.DATABASE_URL: "postgresql://localhost/db",
    ConfigKey.API_KEY: "secret123",
    ConfigKey.DEBUG_MODE: True,
}

# Access with enum or string
assert config[ConfigKey.DATABASE_URL] == "postgresql://localhost/db"
assert config["database_url"] == "postgresql://localhost/db"
```

#### API Status Codes

```python
class HttpStatus(StrEnum):
    OK = auto()
    NOT_FOUND = auto()
    ERROR = auto()

def handle_response(status: HttpStatus):
    if status == "ok":
        return "Success"
    elif status == "not_found":
        return "Resource not found"
    else:
        return "Error occurred"

assert handle_response(HttpStatus.OK) == "Success"
```

#### State Machines

```python
class OrderState(StrEnum):
    CREATED = auto()
    PROCESSING = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

class Order:
    def __init__(self):
        self.state = OrderState.CREATED

    def transition(self, new_state: OrderState):
        # Validate transitions
        valid_transitions = {
            OrderState.CREATED: [OrderState.PROCESSING, OrderState.CANCELLED],
            OrderState.PROCESSING: [OrderState.SHIPPED, OrderState.CANCELLED],
            OrderState.SHIPPED: [OrderState.DELIVERED],
        }

        if new_state not in valid_transitions.get(self.state, []):
            raise ValueError(f"Cannot transition from {self.state} to {new_state}")

        self.state = new_state

order = Order()
order.transition(OrderState.PROCESSING)
assert order.state == "processing"
```

---

## TextType (Deprecated)

⚠️ **DEPRECATED**: `TextType` is deprecated and will be removed in version 0.8.0.

### Overview

`TextType` was a limited enum providing two text type constants. It has been superseded by direct string usage with `TextField`.

**Members:**
- `COLOR_NAME` → `"color_name"`
- `FILE_NAME` → `"file_name"`

### Migration

Replace `TextType` with explicit strings:

```python
# ❌ Old (deprecated)
from factorio.lib.enums import TextType

class OldFactory(Factory[Model]):
    color = fields.TextField(TextType.COLOR_NAME)
    filename = fields.TextField(TextType.FILE_NAME)

# ✅ New (recommended)
class NewFactory(Factory[Model]):
    color = fields.TextField("color_name")
    filename = fields.TextField("file_name")
```

### Why Deprecated?

1. **Limited scope**: Only provided 2 values
2. **Unnecessary abstraction**: Strings are clearer
3. **Better alternative**: Use `TextField` with any Faker provider name directly

See [TextField documentation](fields.md#textfield) for the full list of available text types.

---

## UnstableTextType

⚠️ **UNSTABLE**: This enum is marked as unstable and may change between versions.

### Overview

`UnstableTextType` provides enum constants for 180+ Faker provider names. While convenient, it's marked unstable because:

1. Faker providers may change between versions
2. Not all providers work in all locales
3. Direct string usage is more flexible

### Usage

```python
from factorio.lib.enums import UnstableTextType

class UserFactory(Factory[User]):
    # Using enum constant
    email = fields.TextField(UnstableTextType.EMAIL)

    # Equivalent to using string
    email = fields.TextField("email")
```

### Available Members

**Personal Information:**
- `NAME`, `FIRST_NAME`, `LAST_NAME`, `PREFIX`, `SUFFIX`
- `USER_NAME`, `PASSWORD`

**Contact:**
- `EMAIL`, `SAFE_EMAIL`, `FREE_EMAIL`, `COMPANY_EMAIL`
- `PHONE_NUMBER`, `MSISDN`

**Address:**
- `ADDRESS`, `STREET_ADDRESS`, `CITY`, `COUNTRY`
- `POSTCODE`, `STATE`, `BUILDING_NUMBER`

**Internet:**
- `IPV4`, `IPV6`, `URL`, `DOMAIN_NAME`, `HOSTNAME`
- `MAC_ADDRESS`, `USER_AGENT`

**Business:**
- `COMPANY`, `JOB`, `BS`, `CATCH_PHRASE`
- `EIN`, `DUNS`

**Finance:**
- `CREDIT_CARD_NUMBER`, `IBAN`, `SWIFT`, `BIC`
- `CURRENCY_CODE`, `CURRENCY_NAME`, `PRICE`

**And many more...** (180+ total members)

### Recommendation

Prefer direct string usage over `UnstableTextType`:

```python
# ❌ Unstable - may break if enum changes
class MyFactory(Factory[Model]):
    field = fields.TextField(UnstableTextType.COMPANY)

# ✅ Stable - won't break
class MyFactory(Factory[Model]):
    field = fields.TextField("company")
```

The string approach is:
- More readable
- More flexible
- Less coupled to factorio internals
- Compatible with any Faker provider

---

## Best Practices

### DO:

✅ Use `StrEnum` for configuration keys and status values
✅ Leverage case-insensitive comparison for user input
✅ Use string methods on enum members when needed
✅ Replace `TextType` with direct strings
✅ Prefer strings over `UnstableTextType`

### DON'T:

❌ Use `TextType` (it's deprecated)
❌ Rely on `UnstableTextType` in production code
❌ Mix `StrEnum` with regular `Enum` in comparisons
❌ Assume all Faker providers work in all locales

---

## Examples

### Environment Configuration

```python
class Environment(StrEnum):
    DEVELOPMENT = auto()
    STAGING = auto()
    PRODUCTION = auto()

def get_config(env: Environment):
    configs = {
        "development": {"debug": True, "db": "localhost"},
        "staging": {"debug": True, "db": "staging-db"},
        "production": {"debug": False, "db": "prod-db"},
    }
    return configs[str(env)]

config = get_config(Environment.DEVELOPMENT)
assert config["debug"] is True
```

### Permission System

```python
class Permission(StrEnum):
    READ = auto()
    WRITE = auto()
    DELETE = auto()
    ADMIN = auto()

class User:
    def __init__(self, permissions: set[Permission]):
        self.permissions = permissions

    def has_permission(self, perm: Permission) -> bool:
        return perm in self.permissions or "admin" in self.permissions

user = User({Permission.READ, Permission.WRITE})
assert user.has_permission("read") is True
assert user.has_permission(Permission.DELETE) is False
```

### Workflow States

```python
class TaskStatus(StrEnum):
    TODO = auto()
    IN_PROGRESS = auto()
    REVIEW = auto()
    DONE = auto()

class Task:
    def __init__(self, title: str):
        self.title = title
        self.status = TaskStatus.TODO

    def advance(self):
        transitions = {
            TaskStatus.TODO: TaskStatus.IN_PROGRESS,
            TaskStatus.IN_PROGRESS: TaskStatus.REVIEW,
            TaskStatus.REVIEW: TaskStatus.DONE,
        }
        next_status = transitions.get(self.status)
        if next_status:
            self.status = next_status

task = Task("Write docs")
assert task.status == "todo"
task.advance()
assert task.status == "in_progress"
```

---

## See Also

- [Field Reference](fields.md) - Using enums with TextField
- [Usage Guide](../usage.md) - General usage patterns
- [Faker Providers](https://faker.readthedocs.io/en/master/providers.html) - Complete list of text types
