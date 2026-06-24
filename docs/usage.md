# Usage

## Quick Start

Suppose we have two dataclasses like this:

```python
from dataclasses import dataclass

@dataclass
class Spam:
    a: int
    b: int
    c: int

@dataclass
class Bacon:
    x: int
    y: list[str]
    z: Spam
    t: str = "Francis"
```

We can create factories for them using these factories:

```python
from factorio import fields
from factorio.factories import Factory

class SpamFactory(Factory[Spam]):
    a = fields.IntegerField(max_value=42)
    b = fields.ChoiceField(range(21))
    c = fields.ConstantField(1024)

class BaconFactory(Factory[Bacon]):
    x = fields.IntegerField(max_value=4)
    y = fields.ListField(fields.StringField(max_chars=4), length=5, variation=2)
    z = fields.FactoryField(SpamFactory)
```

Then using the factories is as simple as:

```python
bacon = BaconFactory.build()

assert 0 <= bacon.x <= 4
assert isinstance(bacon.y, list)
assert 0 <= bacon.z.a <= 42
assert bacon.t == "Francis"
```

It is possible to override specific fields:

```python
bacon = BaconFactory.build(x=400, t="Kevin")

assert bacon.x == 400
assert bacon.z.c == 1024
assert bacon.t == "Kevin"
```

Contrary to other common factory libraries, `.build()` is needed to create an object.
This is by design, as we feel that it is more explicit and less error prone.
`MyModelFactory()` should only be reserved to create an actual `MyModelFactory` object
and never for a `MyModel` object.

Also, another difference with other factory libraries, is that this will never try to save
the object to the database. The reason is that we feel that this is not the responsibility
of the factory, and actually should be done by the test itself.

---

## TextField Deep Dive

TextField is one of the most powerful features in factorio. It dynamically delegates to [Faker](https://faker.readthedocs.io/) providers to generate realistic, domain-specific data.

### How It Works

TextField takes a text type name, converts it to lowercase, replaces spaces/hyphens with underscores, and calls the corresponding Faker method:

```python
from factorio import fields

class UserFactory(Factory[User]):
    # These all work:
    email = fields.TextField("email")           # faker.email()
    company = fields.TextField("Company")       # faker.company() (case-insensitive)
    ip_address = fields.TextField("ipv4")       # faker.ipv4()
    full_name = fields.TextField("First Name")  # faker.first_name() (spaces → underscores)
```

### Passing Arguments to Faker

You can pass additional keyword arguments that get forwarded to the Faker method:

```python
class UserFactory(Factory[User]):
    # Custom email domain
    work_email = fields.TextField("safe_email", domain="company.com")
    
    # Paragraph with specific number of sentences
    bio = fields.TextField("paragraph", nb_sentences=3)
    
    # Integer with specific range (via Faker's pyint)
    lucky_number = fields.TextField("pyint", min_value=1, max_value=100)
```

### Common Text Types

**Personal Information:**
- `"name"`, `"first_name"`, `"last_name"`
- `"email"`, `"safe_email"`, `"free_email"`
- `"phone_number"`, `"msisdn"`

**Addresses:**
- `"address"`, `"street_address"`, `"city"`, `"country"`
- `"postcode"`, `"state"`, `"state_abbr"`

**Internet:**
- `"ipv4"`, `"ipv6"`, `"url"`, `"domain_name"`
- `"user_name"`, `"password"`, `"mac_address"`

**Business:**
- `"company"`, `"job"`, `"bs"`, `"catch_phrase"`
- `"ein"`, `"duns"`

**Finance:**
- `"credit_card_number"`, `"iban"`, `"swift"`, `"bic"`
- `"currency_code"`, `"currency_name"`, `"price"`

**Text Generation:**
- `"paragraph"`, `"sentence"`, `"word"`, `"text"`
- `"slug"`, `"locale"`

See [Faker's Providers Documentation](https://faker.readthedocs.io/en/master/providers.html) for the complete list of available providers.

---

## Advanced Field Patterns

### Collection Field Variation

Collection fields (`ListField`, `TupleField`, `SetField`, `DictField`) support a `variation` parameter to randomize their length:

```python
class PostFactory(Factory[Post]):
    # Fixed length: always 5 tags
    fixed_tags = fields.ListField(
        fields.TextField("word"),
        length=5
    )
    
    # Variable length: 3-7 tags (5 ± 2)
    variable_tags = fields.ListField(
        fields.TextField("word"),
        length=5,
        variation=2
    )
    
    # Wide variation: 1-9 items (5 ± 4)
    flexible_items = fields.SetField(
        fields.IntegerField(min_value=1, max_value=100),
        length=5,
        variation=4
    )

post = PostFactory.build()
assert len(post.fixed_tags) == 5
assert 3 <= len(post.variable_tags) <= 7
```

### BooleanField Truth Probability

Control the likelihood of True/False values:

```python
class UserFactory(Factory[User]):
    # 50% chance (default)
    is_active = fields.BooleanField()
    
    # Only 5% chance of being admin
    is_admin = fields.BooleanField(truth_probability=5)
    
    # 95% chance of being verified
    is_verified = fields.BooleanField(truth_probability=95)
    
    # Always False
    is_deleted = fields.BooleanField(truth_probability=0)
    
    # Always True
    is_registered = fields.BooleanField(truth_probability=100)
```

### DecimalField Precision Control

Fine-tune decimal places with `accuracy` and `variation`:

```python
from decimal import Decimal

class ProductFactory(Factory[Product]):
    # Exactly 2 decimal places (for currency)
    price = fields.DecimalField(
        min_value=Decimal("0.01"),
        max_value=Decimal("999.99"),
        accuracy=2,
        variation=0
    )
    
    # 4-6 decimal places (for scientific measurements)
    measurement = fields.DecimalField(
        min_value=0,
        max_value=100,
        accuracy=5,
        variation=1
    )

product = ProductFactory.build()
# price might be: Decimal('45.67')
# measurement might be: Decimal('23.45678')
```

### CharField Alphabet Customization

Generate characters from custom alphabets:

```python
class CodeFactory(Factory[Code]):
    # Lowercase only (a-z)
    lowercase = fields.CharField()
    
    # Mixed case (a-z, A-Z)
    mixed = fields.CharField(include_uppercase=True)
    
    # Alphanumeric (a-z, A-Z, 0-9)
    alphanumeric = fields.CharField(
        include_uppercase=True,
        include_digits=True
    )
    
    # Digits only (0-9) - use CharField + digits
    digit_only = fields.CharField(include_digits=True)

code = CodeFactory.build()
assert code.lowercase in "abcdefghijklmnopqrstuvwxyz"
assert code.alphanumeric in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
```

### TimezoneField Geographic Filtering

Filter timezones by geographic region:

```python
from zoneinfo import ZoneInfo

class UserFactory(Factory[User]):
    # Any timezone worldwide
    any_timezone = fields.TimezoneField()
    
    # Only European timezones
    eu_timezone = fields.TimezoneField(areas=("Europe",))
    
    # American or European timezones
    western_timezone = fields.TimezoneField(
        areas=("America", "Europe")
    )
    
    # Asia-Pacific region
    apac_timezone = fields.TimezoneField(
        areas=("Asia", "Australia", "Pacific")
    )
    
    # UTC only (via "Etc" area)
    utc_timezone = fields.TimezoneField(areas=("Etc",))

user = UserFactory.build()
assert user.eu_timezone.key.startswith("Europe/")
assert user.apac_timezone.key.split("/")[0] in ("Asia", "Australia", "Pacific")
```

**Available geographic areas:**
- `"Africa"`, `"America"`, `"Antarctica"`, `"Arctic"`, `"Asia"`
- `"Atlantic"`, `"Australia"`, `"Europe"`, `"Indian"`, `"Pacific"`
- `"Etc"` (includes UTC and special zones)

---

## Field Override Techniques

### Override with Values

The simplest way to override fields is by passing values directly:

```python
class UserFactory(Factory[User]):
    name = fields.TextField("name")
    age = fields.IntegerField(min_value=18, max_value=65)
    email = fields.TextField("email")

# Override specific fields
user = UserFactory.build(
    name="John Doe",
    age=30,
    email="john@example.com"
)

assert user.name == "John Doe"
assert user.age == 30
```

### Override with Field Instances

For dynamic ranges or conditional logic, override with field instances:

```python
# Generate users in specific age ranges
young_user = UserFactory.build(
    age=fields.IntegerField(min_value=18, max_value=25)
)

senior_user = UserFactory.build(
    age=fields.IntegerField(min_value=60, max_value=65)
)

# Dynamic based on test context
def create_user_for_region(region: str):
    if region == "EU":
        return UserFactory.build(
            age=fields.IntegerField(min_value=18, max_value=100)  # GDPR allows all ages
        )
    else:
        return UserFactory.build(
            age=fields.IntegerField(min_value=18, max_value=65)
        )
```

### Combining Overrides

Mix value overrides and field overrides:

```python
user = UserFactory.build(
    name="Jane Smith",  # Static value
    age=fields.IntegerField(min_value=25, max_value=30),  # Dynamic range
    email="jane@test.com"  # Static value
)
```

---

## Nested Factories

### Basic FactoryField

Use `FactoryField` to generate nested objects:

```python
from dataclasses import dataclass
from factorio import fields
from factorio.factories import Factory

@dataclass
class Address:
    street: str
    city: str
    zipcode: str

@dataclass
class User:
    name: str
    email: str
    address: Address

class AddressFactory(Factory[Address]):
    street = fields.TextField("street_address")
    city = fields.TextField("city")
    zipcode = fields.TextField("postcode")

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    address = fields.FactoryField(AddressFactory)

user = UserFactory.build()
assert isinstance(user.address, Address)
assert isinstance(user.address.city, str)
```

### Complex Object Graphs

Nest factories multiple levels deep:

```python
@dataclass
class Country:
    name: str
    code: str

@dataclass
class Address:
    street: str
    city: str
    country: Country

@dataclass
class User:
    name: str
    address: Address

class CountryFactory(Factory[Country]):
    name = fields.TextField("country")
    code = fields.TextField("country_code")

class AddressFactory(Factory[Address]):
    street = fields.TextField("street_address")
    city = fields.TextField("city")
    country = fields.FactoryField(CountryFactory)

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    address = fields.FactoryField(AddressFactory)

user = UserFactory.build()
assert isinstance(user.address.country, Country)
assert isinstance(user.address.country.code, str)
```

### Overriding Nested Fields

Use double underscore notation to override nested factory fields:

```python
# Override nested address fields
user = UserFactory.build(
    address__city="Custom City",
    address__country__name="Custom Country"
)

assert user.address.city == "Custom City"
assert user.address.country.name == "Custom Country"
```

**Note:** This requires your model to support `**kwargs` initialization or you need to handle nested overrides manually.

---

## Factory Inheritance

### Extending Base Factories

Create base factories and extend them:

```python
class BaseUserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    is_active = fields.BooleanField(truth_probability=90)

class AdminUserFactory(BaseUserFactory):
    is_admin = fields.ConstantField(True)
    role = fields.ConstantField("administrator")

class RegularUserFactory(BaseUserFactory):
    is_admin = fields.ConstantField(False)
    role = fields.ChoiceField(["user", "member", "subscriber"])

admin = AdminUserFactory.build()
assert admin.is_admin is True
assert admin.role == "administrator"

regular = RegularUserFactory.build()
assert regular.is_admin is False
assert regular.role in ["user", "member", "subscriber"]
```

### Overriding Parent Fields

Child factories can override parent field definitions:

```python
class BaseProductFactory(Factory[Product]):
    name = fields.TextField("word")
    price = fields.DecimalField(min_value=1, max_value=100, accuracy=2)
    category = fields.ChoiceField(["general", "misc"])

class PremiumProductFactory(BaseProductFactory):
    # Override price range for premium products
    price = fields.DecimalField(min_value=100, max_value=1000, accuracy=2)
    
    # Override category
    category = fields.ConstantField("premium")
    
    # Add new field
    warranty_years = fields.IntegerField(min_value=2, max_value=5)

premium = PremiumProductFactory.build()
assert 100 <= premium.price <= 1000
assert premium.category == "premium"
assert 2 <= premium.warranty_years <= 5
```

### Multiple Inheritance

Combine multiple base factories (use with caution):

```python
class TimestampedFactory(Factory[T]):
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

class AuditableFactory(Factory[T]):
    created_by = fields.TextField("user_name")
    updated_by = fields.TextField("user_name")

class ProductFactory(TimestampedFactory, AuditableFactory):
    name = fields.TextField("word")
    price = fields.DecimalField(min_value=1, max_value=100)

product = ProductFactory.build()
assert hasattr(product, 'created_at')
assert hasattr(product, 'created_by')
assert hasattr(product, 'name')
```

**Warning:** Multiple inheritance can lead to conflicts if both parents define the same fields. Python's MRO (Method Resolution Order) determines which field wins.

---

## Design Philosophy

### Explicit .build() Method

Unlike some factory libraries, factorio requires explicit `.build()` calls:

```python
# ✅ Correct - explicit object creation
user = UserFactory.build()

# ❌ Wrong - this creates a Factory instance, not a User
user = UserFactory()  # Returns UserFactory object
```

**Why?** This makes code more explicit and prevents accidental factory instantiation when you meant to create model objects.

### No Database Interaction

factorio never saves objects to databases:

```python
# Creates object in memory only
user = UserFactory.build()

# You must explicitly save if needed
session.add(user)
session.commit()
```

**Why?** Separation of concerns - factories should generate data, tests should handle persistence. This makes tests faster and more predictable.

### Realistic Data with Faker

Under the hood, factorio uses [Faker](https://github.com/joke2k/faker) to generate realistic test data:

```python
# Instead of unrealistic data like:
user = User(name="test1", email="test@example.com")

# You get realistic data:
user = UserFactory.build()
# user.name might be "Sarah Johnson"
# user.email might be "sarah.johnson@company.net"
```

This helps catch bugs that only appear with realistic data patterns.
