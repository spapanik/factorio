# Field Reference

Complete reference for all available field types in factorio. Fields are the building blocks of factories, defining how each attribute of your model should be generated.

## Base Classes

### AbstractField[T]

The abstract base class that all fields inherit from. This defines the interface that all concrete fields must implement.

**Methods:**
- `__init__(*args, **kwargs)`: Initialize the field with configuration parameters
- `__call__() -> T`: Generate and return a value

**Note:** You should not use `AbstractField` directly. Instead, use one of the concrete field implementations below.

---

## Primitive Fields

### ConstantField[T]

Returns a fixed, constant value every time it's called.

**Parameters:**
- `value: T` - The constant value to return

**Example:**
```python
from factorio import fields

class UserFactory(Factory[User]):
    status = fields.ConstantField("active")
    version = fields.ConstantField(1)

user = UserFactory.build()
assert user.status == "active"
assert user.version == 1
```

**Use when:** You need a field to always have the same value across all instances.

---

### ChoiceField[T]

Randomly selects a value from a provided set of options.

**Parameters:**
- `options: Iterable[T]` - Collection of possible values to choose from

**Example:**
```python
from factorio import fields

class ProductFactory(Factory[Product]):
    category = fields.ChoiceField(["electronics", "books", "clothing"])
    rating = fields.ChoiceField(range(1, 6))  # 1-5 stars

product = ProductFactory.build()
assert product.category in ["electronics", "books", "clothing"]
assert 1 <= product.rating <= 5
```

**Use when:** A field should have one of several predefined values.

---

### BooleanField

Generates boolean values (True/False) with configurable probability.

**Parameters:**
- `truth_probability: int = 50` - Percentage chance of returning True (0-100)

**Example:**
```python
from factorio import fields

class UserFactory(Factory[User]):
    is_active = fields.BooleanField()  # 50% chance of True
    is_admin = fields.BooleanField(truth_probability=10)  # 10% chance of True
    is_verified = fields.BooleanField(truth_probability=90)  # 90% chance of True

user = UserFactory.build()
assert isinstance(user.is_active, bool)
```

**Use when:** You need boolean fields with specific true/false distributions.

---

### IntegerField

Generates random integers within a specified range.

**Parameters:**
- `min_value: int = 1` - Minimum value (inclusive)
- `max_value: int = 9999` - Maximum value (inclusive)
- `step: int = 1` - Step size between values

**Example:**
```python
from factorio import fields

class ProductFactory(Factory[Product]):
    quantity = fields.IntegerField(min_value=1, max_value=100)
    price_cents = fields.IntegerField(min_value=100, max_value=99999, step=100)
    even_number = fields.IntegerField(min_value=0, max_value=100, step=2)

product = ProductFactory.build()
assert 1 <= product.quantity <= 100
assert product.price_cents % 100 == 0
```

**Use when:** You need integer values within a specific range.

---

### DecimalField

Generates random Decimal values with controlled precision.

**Parameters:**
- `min_value: float | Decimal = 0` - Minimum value
- `max_value: float | Decimal = 9999` - Maximum value
- `accuracy: int = 3` - Base number of decimal places
- `variation: int = 0` - Variation in decimal places (actual = accuracy ± variation)

**Example:**
```python
from factorio import fields
from decimal import Decimal

class ProductFactory(Factory[Product]):
    price = fields.DecimalField(
        min_value=Decimal("0.01"),
        max_value=Decimal("999.99"),
        accuracy=2
    )
    # Generates prices like 45.67, 123.45, etc.

    precise_value = fields.DecimalField(
        min_value=0,
        max_value=1,
        accuracy=6,
        variation=2
    )
    # Generates values with 4-8 decimal places

product = ProductFactory.build()
assert isinstance(product.price, Decimal)
```

**Use when:** You need precise decimal values, especially for financial calculations.

---

### FloatField

Generates random floating-point numbers within a range.

**Parameters:**
- `min_value: float = 0` - Minimum value
- `max_value: float = 9999` - Maximum value

**Example:**
```python
from factorio import fields

class SensorFactory(Factory[Sensor]):
    temperature = fields.FloatField(min_value=-40.0, max_value=120.0)
    humidity = fields.FloatField(min_value=0.0, max_value=100.0)

sensor = SensorFactory.build()
assert -40.0 <= sensor.temperature <= 120.0
```

**Use when:** You need floating-point values and exact decimal precision is not critical.

---

### CharField

Generates a single character from a configurable alphabet.

**Parameters:**
- `include_uppercase: bool = False` - Include uppercase letters (A-Z)
- `include_digits: bool = False` - Include digits (0-9)

**Default alphabet:** Lowercase letters (a-z)

**Example:**
```python
from factorio import fields

class CodeFactory(Factory[Code]):
    lowercase_letter = fields.CharField()  # a-z
    mixed_case = fields.CharField(include_uppercase=True)  # a-z, A-Z
    alphanumeric = fields.CharField(include_uppercase=True, include_digits=True)  # a-z, A-Z, 0-9

code = CodeFactory.build()
assert len(code.lowercase_letter) == 1
assert code.alphanumeric in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
```

**Use when:** You need single characters, such as grade letters, status codes, or building blocks for strings.

---

### StringField

Generates random strings with configurable length and optional prefix/suffix.

**Parameters:**
- `min_chars: int = 1` - Minimum string length
- `max_chars: int = 20` - Maximum string length
- `prefix: str = ""` - String prefix to prepend
- `suffix: str = ""` - String suffix to append

**Example:**
```python
from factorio import fields

class UserFactory(Factory[User]):
    username = fields.StringField(min_chars=5, max_chars=15)
    user_id = fields.StringField(min_chars=8, max_chars=8, prefix="USR-")
    filename = fields.StringField(min_chars=5, max_chars=10, suffix=".txt")

user = UserFactory.build()
assert 5 <= len(user.username) <= 15
assert user.user_id.startswith("USR-")
assert user.filename.endswith(".txt")
```

**Use when:** You need random strings for names, IDs, descriptions, etc.

---

## Date/Time Fields

### DateTimeField

Generates timezone-aware datetime objects.

**Parameters:**
- `min_datetime: datetime = datetime(2010, 1, 1, tzinfo=UTC)` - Minimum datetime
- `max_datetime: datetime = datetime(2030, 12, 31, tzinfo=UTC)` - Maximum datetime

**Note:** The timezone from `min_datetime` is used for all generated values.

**Example:**
```python
from factorio import fields
from datetime import datetime
from zoneinfo import ZoneInfo

class EventFactory(Factory[Event]):
    created_at = fields.DateTimeField()  # 2010-2030, UTC
    meeting_time = fields.DateTimeField(
        min_datetime=datetime(2024, 1, 1, tzinfo=ZoneInfo("America/New_York")),
        max_datetime=datetime(2024, 12, 31, tzinfo=ZoneInfo("America/New_York"))
    )

event = EventFactory.build()
assert event.created_at.tzinfo is not None  # Timezone-aware
```

**Use when:** You need timezone-aware datetimes for timestamps, events, etc.

---

### NaiveDateTimeField

Generates timezone-naive datetime objects (no timezone information).

**Parameters:**
- `min_datetime: datetime = datetime(2010, 1, 1)` - Minimum datetime (naive)
- `max_datetime: datetime = datetime(2030, 12, 31)` - Maximum datetime (naive)

**Example:**
```python
from factorio import fields
from datetime import datetime

class LogFactory(Factory[Log]):
    timestamp = fields.NaiveDateTimeField(
        min_datetime=datetime(2024, 1, 1),
        max_datetime=datetime(2024, 6, 30)
    )

log = LogFactory.build()
assert log.timestamp.tzinfo is None  # No timezone
```

**Use when:** You need naive datetimes (common in databases that don't store timezone info).

**Warning:** Naive datetimes can lead to ambiguity. Prefer `DateTimeField` when possible.

---

### DateField

Generates date objects (without time component).

**Parameters:**
- `min_date: date = date(2010, 1, 1)` - Minimum date
- `max_date: date = date(2030, 12, 31)` - Maximum date

**Example:**
```python
from factorio import fields
from datetime import date

class UserFactory(Factory[User]):
    birth_date = fields.DateField(
        min_date=date(1970, 1, 1),
        max_date=date(2005, 12, 31)
    )
    signup_date = fields.DateField(
        min_date=date(2020, 1, 1),
        max_date=date(2024, 12, 31)
    )

user = UserFactory.build()
assert isinstance(user.birth_date, date)
assert user.birth_date.year < 2006
```

**Use when:** You need dates without time components (birthdays, anniversaries, etc.).

---

### TimeField

Generates time objects within a specified range.

**Parameters:**
- `min_time: time = time(0)` - Minimum time (midnight)
- `max_time: time = time(23, 59, 59, 999999)` - Maximum time (end of day)

**Example:**
```python
from factorio import fields
from datetime import time

class ScheduleFactory(Factory[Schedule]):
    start_time = fields.TimeField(
        min_time=time(9, 0),  # 9 AM
        max_time=time(17, 0)  # 5 PM
    )
    lunch_time = fields.TimeField(
        min_time=time(11, 30),
        max_time=time(13, 30)
    )

schedule = ScheduleFactory.build()
assert isinstance(schedule.start_time, time)
```

**Use when:** You need time-of-day values without date components.

---

### TimedeltaField

Generates timedelta objects representing time durations.

**Parameters:**
- `min_timedelta: timedelta = timedelta(0)` - Minimum duration
- `max_timedelta: timedelta = timedelta(days=365)` - Maximum duration

**Example:**
```python
from factorio import fields
from datetime import timedelta

class SubscriptionFactory(Factory[Subscription]):
    duration = fields.TimedeltaField(
        min_timedelta=timedelta(days=30),
        max_timedelta=timedelta(days=365)
    )
    trial_period = fields.TimedeltaField(
        min_timedelta=timedelta(hours=1),
        max_timedelta=timedelta(days=14)
    )

subscription = SubscriptionFactory.build()
assert isinstance(subscription.duration, timedelta)
```

**Use when:** You need time durations (subscription lengths, timeouts, etc.).

---

### TimezoneField

Generates ZoneInfo timezone objects, optionally filtered by geographic area.

**Parameters:**
- `areas: tuple[str, ...] = ()` - Geographic areas to filter by. Empty tuple means all areas.

**Available areas:**
- `"Africa"`, `"America"`, `"Antarctica"`, `"Arctic"`, `"Asia"`
- `"Atlantic"`, `"Australia"`, `"Europe"`, `"Indian"`, `"Pacific"`
- `"Etc"` (includes UTC and other special zones)

**Example:**
```python
from factorio import fields
from zoneinfo import ZoneInfo

class UserFactory(Factory[User]):
    # Any timezone
    timezone = fields.TimezoneField()

    # Only European timezones
    eu_timezone = fields.TimezoneField(areas=("Europe",))

    # American or European timezones
    western_timezone = fields.TimezoneField(areas=("America", "Europe"))

    # Only UTC
    utc_only = fields.TimezoneField(areas=("Etc",))

user = UserFactory.build()
assert isinstance(user.timezone, ZoneInfo)
assert user.eu_timezone.key.startswith("Europe/")
```

**Use when:** You need timezone objects for international applications.

---

## Collection Fields

### ListField[T]

Generates lists containing values from a nested field.

**Parameters:**
- `field: AbstractField[T]` - The field type for list items
- `length: int = 5` - Target list length
- `variation: int = 0` - Length variation (actual length = length ± variation)

**Example:**
```python
from factorio import fields

class UserFactory(Factory[User]):
    # Fixed length list
    tags = fields.ListField(fields.StringField(max_chars=10), length=3)

    # Variable length list (3-7 items)
    scores = fields.ListField(
        fields.IntegerField(min_value=0, max_value=100),
        length=5,
        variation=2
    )

user = UserFactory.build()
assert len(user.tags) == 3
assert 3 <= len(user.scores) <= 7
assert all(isinstance(score, int) for score in user.scores)
```

**Use when:** You need lists of homogeneous values.

---

### TupleField[T]

Generates tuples containing values from a nested field.

**Parameters:**
- `field: AbstractField[T]` - The field type for tuple items
- `length: int = 5` - Target tuple length
- `variation: int = 0` - Length variation (actual length = length ± variation)

**Example:**
```python
from factorio import fields

class DataFactory(Factory[Data]):
    coordinates = fields.TupleField(
        fields.FloatField(min_value=-180, max_value=180),
        length=2
    )
    # Generates tuples like (45.67, -123.45)

data = DataFactory.build()
assert isinstance(data.coordinates, tuple)
assert len(data.coordinates) == 2
```

**Use when:** You need immutable sequences (tuples instead of lists).

---

### SetField[T]

Generates sets containing unique values from a nested field.

**Parameters:**
- `field: AbstractField[T]` - The field type for set items
- `length: int = 5` - Target set size
- `variation: int = 0` - Size variation (actual size = length ± variation)

**Note:** Since sets contain unique values, the actual size may be less than expected if the field generates duplicate values.

**Example:**
```python
from factorio import fields

class UserFactory(Factory[User]):
    # Set of unique tags
    unique_tags = fields.SetField(
        fields.StringField(min_chars=3, max_chars=8),
        length=5
    )

user = UserFactory.build()
assert isinstance(user.unique_tags, set)
assert len(user.unique_tags) <= 5  # May be less due to uniqueness
```

**Use when:** You need collections of unique values.

---

### DictField[K, V]

Generates dictionaries with keys and values from separate field generators.

**Parameters:**
- `key_field: AbstractField[K]` - Field type for dictionary keys
- `value_field: AbstractField[T]` - Field type for dictionary values
- `length: int = 5` - Target dictionary size
- `variation: int = 0` - Size variation (actual size = length ± variation)

**Example:**
```python
from factorio import fields

class ConfigFactory(Factory[Config]):
    settings = fields.DictField(
        key_field=fields.StringField(min_chars=3, max_chars=10),
        value_field=fields.IntegerField(min_value=0, max_value=100),
        length=5
    )

config = ConfigFactory.build()
assert isinstance(config.settings, dict)
assert len(config.settings) == 5
for key, value in config.settings.items():
    assert isinstance(key, str)
    assert isinstance(value, int)
```

**Use when:** You need key-value mappings with generated keys and values.

---

## Special Fields

### TextField

Dynamically delegates to Faker providers to generate realistic text data. This is one of the most powerful fields in factorio.

**Parameters:**
- `text_type: str` - Name of the Faker provider method (case-insensitive)
- `**kwargs` - Additional arguments passed to the Faker method

**How it works:**
TextField converts the `text_type` parameter to lowercase, replaces spaces/hyphens with underscores, and calls the corresponding Faker method. For example:
- `"email"` → `faker.email()`
- `"company"` → `faker.company()`
- `"ipv4"` → `faker.ipv4()`
- `"First Name"` → `faker.first_name()`

**Example:**
```python
from factorio import fields

class UserFactory(Factory[User]):
    email = fields.TextField("email")
    company = fields.TextField("company")
    ip_address = fields.TextField("ipv4")
    full_name = fields.TextField("name")
    phone = fields.TextField("phone_number")
    country = fields.TextField("country")

    # With kwargs
    safe_email = fields.TextField("safe_email", domain="example.com")
    paragraph = fields.TextField("paragraph", nb_sentences=3)

user = UserFactory.build()
assert "@" in user.email
assert isinstance(user.company, str)
```

**Common text types:**
- Personal: `"name"`, `"first_name"`, `"last_name"`, `"email"`, `"phone_number"`
- Address: `"address"`, `"city"`, `"country"`, `"postcode"`, `"street_address"`
- Company: `"company"`, `"job"`, `"bs"`, `"catch_phrase"`
- Internet: `"ipv4"`, `"ipv6"`, `"url"`, `"domain_name"`, `"user_name"`
- Finance: `"credit_card_number"`, `"iban"`, `"swift"`, `"currency_code"`
- Text: `"paragraph"`, `"sentence"`, `"word"`, `"text"`

See [Faker's documentation](https://faker.readthedocs.io/en/master/providers.html) for a complete list of providers.

**Use when:** You need realistic, domain-specific text data.

---

### FactoryField[T]

Nests another factory to generate complex object graphs.

**Parameters:**
- `factory: type[Factory[T]]` - The factory class to use for generating the nested object

**Example:**
```python
from factorio import fields
from factorio.factories import Factory
from dataclasses import dataclass

@dataclass
class Address:
    street: str
    city: str
    country: str

@dataclass
class User:
    name: str
    address: Address

class AddressFactory(Factory[Address]):
    street = fields.TextField("street_address")
    city = fields.TextField("city")
    country = fields.TextField("country")

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    address = fields.FactoryField(AddressFactory)

user = UserFactory.build()
assert isinstance(user.address, Address)
assert isinstance(user.address.city, str)
```

**Use when:** Your model contains nested objects that also need to be generated.

**Advanced usage:**
You can override nested factory fields using dot notation:
```python
user = UserFactory.build(address__city="Custom City")
```

---

## Tips and Best Practices

### Combining Fields

Fields can be combined to create complex data structures:

```python
class ComplexFactory(Factory[ComplexModel]):
    # List of dicts
    metadata = fields.ListField(
        fields.DictField(
            key_field=fields.StringField(max_chars=10),
            value_field=fields.StringField(max_chars=50),
            length=3
        ),
        length=5
    )

    # Tuple of nested factories
    locations = fields.TupleField(
        fields.FactoryField(AddressFactory),
        length=2
    )
```

### Field Override

You can override any field when calling `.build()`:

```python
# Override with a value
user = UserFactory.build(name="John Doe")

# Override with another field (for dynamic ranges)
user = UserFactory.build(age=fields.IntegerField(min_value=50, max_value=60))
```

### Performance Considerations

- `ConstantField` is the fastest (no generation needed)
- `TextField` may be slower due to Faker method lookup
- Nested `FactoryField` creates entire object graphs (use sparingly in large tests)
- Collection fields with high `variation` may take longer due to uniqueness constraints in `SetField`
