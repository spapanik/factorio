# Cookbook

Common patterns and recipes for using factorio effectively in your tests.

## Generating Unique Values

### Sequential IDs

Use a counter to generate unique sequential values:

```python
from factorio import fields
from factorio.factories import Factory

_counter = 0

def next_id():
    global _counter
    _counter += 1
    return _counter

class UserFactory(Factory[User]):
    user_id = fields.ConstantField(None)  # Will be overridden

    @classmethod
    def build(cls, **kwargs):
        if 'user_id' not in kwargs:
            kwargs['user_id'] = next_id()
        return super().build(**kwargs)

# Usage
user1 = UserFactory.build()  # user_id = 1
user2 = UserFactory.build()  # user_id = 2
user3 = UserFactory.build()  # user_id = 3
```

### UUID Generation

```python
import uuid
from factorio import fields

class EntityFactory(Factory[Entity]):
    id = fields.ConstantField(str(uuid.uuid4()))

# Each entity gets a unique UUID
entity1 = EntityFactory.build()
entity2 = EntityFactory.build()
assert entity1.id != entity2.id
```

### Unique Emails

```python
_email_counter = 0

def unique_email():
    global _email_counter
    _email_counter += 1
    return f"user{_email_counter}@example.com"

class UserFactory(Factory[User]):
    email = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        if 'email' not in kwargs:
            kwargs['email'] = unique_email()
        return super().build(**kwargs)

# All emails are unique
users = [UserFactory.build() for _ in range(100)]
emails = [u.email for u in users]
assert len(emails) == len(set(emails))  # No duplicates
```

## Conditional Field Generation

### Based on Other Fields

Generate values conditionally based on other field values:

```python
from factorio import fields
from factorio.factories import Factory

class UserFactory(Factory[User]):
    age = fields.IntegerField(min_value=0, max_value=100)
    is_adult = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)
        # Set is_adult based on age
        instance.is_adult = instance.age >= 18
        return instance

user = UserFactory.build(age=25)
assert user.is_adult is True

user = UserFactory.build(age=15)
assert user.is_adult is False
```

### Random Selection from Categories

```python
class ProductFactory(Factory[Product]):
    category = fields.ChoiceField(["electronics", "books", "clothing"])
    subcategory = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)

        # Set subcategory based on category
        if instance.category == "electronics":
            instance.subcategory = "phones"
        elif instance.category == "books":
            instance.subcategory = "fiction"
        else:
            instance.subcategory = "shirts"

        return instance
```

## Lazy Evaluation

### Deferred Computation

Use lambda or callable for lazy evaluation:

```python
from datetime import datetime

class EventFactory(Factory[Event]):
    created_at = fields.DateTimeField()
    updated_at = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)
        # Set updated_at to current time (lazy)
        if instance.updated_at is None:
            instance.updated_at = datetime.utcnow()
        return instance
```

### Dynamic Ranges

```python
class SalaryFactory(Factory[Salary]):
    base_salary = fields.IntegerField(min_value=30000, max_value=50000)
    bonus_percentage = fields.IntegerField(min_value=5, max_value=20)
    total_compensation = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)
        # Calculate based on generated values
        instance.total_compensation = int(
            instance.base_salary * (1 + instance.bonus_percentage / 100)
        )
        return instance
```

## Testing with Realistic Data

### Realistic Names and Addresses

```python
class CustomerFactory(Factory[Customer]):
    first_name = fields.TextField("first_name")
    last_name = fields.TextField("last_name")
    full_name = fields.ConstantField(None)
    email = fields.TextField("safe_email")
    phone = fields.TextField("phone_number")
    address = fields.TextField("address")
    city = fields.TextField("city")
    country = fields.TextField("country")
    postcode = fields.TextField("postcode")

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)
        instance.full_name = f"{instance.first_name} {instance.last_name}"
        return instance

customer = CustomerFactory.build()
assert customer.full_name  # "John Smith"
assert "@" in customer.email  # "john.smith@example.com"
assert customer.phone  # "+1-555-123-4567"
```

### Realistic Financial Data

```python
from decimal import Decimal

class TransactionFactory(Factory[Transaction]):
    amount = fields.DecimalField(
        min_value=Decimal("0.01"),
        max_value=Decimal("9999.99"),
        accuracy=2
    )
    currency = fields.ChoiceField(["USD", "EUR", "GBP", "JPY"])
    description = fields.TextField("sentence", nb_words=8)
    timestamp = fields.DateTimeField()

transaction = TransactionFactory.build()
assert isinstance(transaction.amount, Decimal)
assert transaction.currency in ["USD", "EUR", "GBP", "JPY"]
```

### Realistic Internet Data

```python
class WebsiteFactory(Factory[Website]):
    domain = fields.TextField("domain_name")
    url = fields.TextField("url")
    ip_address = fields.TextField("ipv4")
    user_agent = fields.TextField("user_agent")
    email = fields.TextField("company_email")

website = WebsiteFactory.build()
assert website.url.startswith("http")
assert "." in website.ip_address  # Valid IP format
```

## Performance Considerations

### Bulk Generation

For large datasets, generate in batches:

```python
def test_large_dataset():
    # Generate 1000 users efficiently
    users = [UserFactory.build() for _ in range(1000)]

    assert len(users) == 1000
    assert all(isinstance(u, User) for u in users)
```

**Tip:** List comprehensions are faster than loops for bulk generation.

### Avoid Unnecessary Nested Factories

```python
# ❌ Slow - creates entire object graph
class SlowOrderFactory(Factory[Order]):
    customer = fields.FactoryField(CustomerFactory)
    items = fields.ListField(fields.FactoryField(ItemFactory), length=10)
    shipping_address = fields.FactoryField(AddressFactory)
    billing_address = fields.FactoryField(AddressFactory)

# ✅ Faster - only generate what you need
class FastOrderFactory(Factory[Order]):
    customer_id = fields.IntegerField(min_value=1, max_value=1000)
    item_count = fields.IntegerField(min_value=1, max_value=10)
    total_amount = fields.DecimalField(min_value=1, max_value=999)

def test_performance():
    import time

    start = time.time()
    orders = [FastOrderFactory.build() for _ in range(1000)]
    elapsed = time.time() - start

    print(f"Generated 1000 orders in {elapsed:.2f}s")
```

### Cache Reusable Factories

```python
# Create factory once, reuse many times
user_factory = UserFactory

def test_multiple_scenarios():
    # Reuse same factory
    user1 = user_factory.build()
    user2 = user_factory.build()
    user3 = user_factory.build()
```

## Debugging Factory Issues

### Inspect Generated Values

```python
def debug_factory():
    user = UserFactory.build()

    # Print all fields
    print(f"Name: {user.name}")
    print(f"Email: {user.email}")
    print(f"Age: {user.age}")

    # Or convert to dict if supported
    if hasattr(user, '__dict__'):
        print(user.__dict__)
```

### Test Field Ranges

```python
def test_field_ranges():
    # Generate many instances to verify distribution
    ages = [UserFactory.build().age for _ in range(100)]

    assert min(ages) >= 18
    assert max(ages) <= 65
    assert len(set(ages)) > 10  # Good variety

    print(f"Age range: {min(ages)}-{max(ages)}")
    print(f"Unique values: {len(set(ages))}")
```

### Verify Type Correctness

```python
def test_types():
    user = UserFactory.build()

    assert isinstance(user.name, str), f"Expected str, got {type(user.name)}"
    assert isinstance(user.age, int), f"Expected int, got {type(user.age)}"
    assert isinstance(user.email, str), f"Expected str, got {type(user.email)}"
```

## Common Patterns

### Timestamped Models

```python
from datetime import datetime

class TimestampedFactory(Factory[T]):
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

    @classmethod
    def build(cls, **kwargs):
        # Ensure updated_at >= created_at
        instance = super().build(**kwargs)
        if instance.updated_at < instance.created_at:
            instance.updated_at = instance.created_at
        return instance

class ArticleFactory(TimestampedFactory):
    title = fields.TextField("sentence")
    content = fields.TextField("paragraphs", nb=3)
```

### Soft Delete Pattern

```python
class SoftDeletableFactory(Factory[T]):
    is_deleted = fields.BooleanField(truth_probability=10)  # 10% deleted
    deleted_at = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)
        if instance.is_deleted and instance.deleted_at is None:
            instance.deleted_at = datetime.utcnow()
        return instance

class PostFactory(SoftDeletableFactory):
    title = fields.TextField("sentence")
    content = fields.TextField("paragraph")
```

### Versioned Models

```python
class VersionedFactory(Factory[T]):
    version = fields.IntegerField(min_value=1, max_value=10)
    is_latest = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)
        instance.is_latest = instance.version == 10
        return instance
```

### Enum-Like Fields

```python
class OrderFactory(Factory[Order]):
    status = fields.ChoiceField([
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled"
    ])
    priority = fields.ChoiceField(["low", "medium", "high", "critical"])

order = OrderFactory.build()
assert order.status in ["pending", "processing", "shipped", "delivered", "cancelled"]
```

## Integration with pytest

### pytest Fixtures with Factories

```python
import pytest

@pytest.fixture
def user():
    return UserFactory.build()

@pytest.fixture
def admin_user():
    return UserFactory.build(
        is_admin=True,
        role="administrator"
    )

@pytest.fixture
def multiple_users():
    return [UserFactory.build() for _ in range(5)]

def test_with_fixture(user):
    assert user.name
    assert user.email

def test_admin(admin_user):
    assert admin_user.is_admin is True

def test_bulk(multiple_users):
    assert len(multiple_users) == 5
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("age_range", [
    (18, 25),
    (26, 40),
    (41, 65),
])
def test_age_groups(age_range):
    min_age, max_age = age_range
    user = UserFactory.build(
        age=fields.IntegerField(min_value=min_age, max_value=max_age)
    )

    assert min_age <= user.age <= max_age
```

### Factory as pytest Fixture

```python
@pytest.fixture
def user_factory():
    return UserFactory

def test_custom_user(user_factory):
    user = user_factory.build(name="Custom Name")
    assert user.name == "Custom Name"
```

## Best Practices Summary

### DO:

✅ Use realistic data with TextField
✅ Override fields for specific test scenarios
✅ Keep factories simple and focused
✅ Use collection variation for realistic diversity
✅ Document non-obvious field choices
✅ Test edge cases with explicit overrides

### DON'T:

❌ Hardcode values in factories (use fields instead)
❌ Create overly complex factory hierarchies
❌ Ignore type hints
❌ Generate unnecessarily large object graphs
❌ Forget that `.build()` is required
❌ Assume database persistence happens automatically

### Quick Reference

```python
# Basic factory
class MyFactory(Factory[MyModel]):
    field1 = fields.TextField("word")
    field2 = fields.IntegerField(min_value=1, max_value=100)
    field3 = fields.BooleanField(truth_probability=80)

# Build instance
instance = MyFactory.build()

# Override fields
instance = MyFactory.build(field1="custom", field2=42)

# Nested factories
class ParentFactory(Factory[Parent]):
    child = fields.FactoryField(ChildFactory)

# Collections
items = fields.ListField(fields.StringField(), length=5, variation=2)
```
