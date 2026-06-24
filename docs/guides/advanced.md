# Advanced Usage Guide

Advanced patterns and techniques for getting the most out of factorio.

## Complex Field Compositions

### Nested Collections

Combine collection fields to create complex data structures:

```python
from factorio import fields
from factorio.factories import Factory

@dataclass
class Matrix:
    rows: list[list[int]]

class MatrixFactory(Factory[Matrix]):
    rows = fields.ListField(
        field=fields.ListField(
            field=fields.IntegerField(min_value=0, max_value=100),
            length=3
        ),
        length=3
    )
    # Generates 3x3 matrices like:
    # [[45, 67, 23], [12, 89, 34], [56, 78, 90]]

matrix = MatrixFactory.build()
assert len(matrix.rows) == 3
assert all(len(row) == 3 for row in matrix.rows)
```

### Mixed-Type Dictionaries

Create dictionaries with varied key/value types:

```python
@dataclass
class Config:
    settings: dict[str, object]

class ConfigFactory(Factory[Config]):
    settings = fields.DictField(
        key_field=fields.StringField(min_chars=3, max_chars=10),
        value_field=fields.ChoiceField([
            fields.IntegerField(min_value=1, max_value=100),
            fields.TextField("word"),
            fields.BooleanField(),
        ]),
        length=5
    )

config = ConfigFactory.build()
for key, value in config.settings.items():
    assert isinstance(key, str)
    assert isinstance(value, (int, str, bool))
```

**Note:** The above won't work directly because `ChoiceField` expects values, not fields. Instead:

```python
class ConfigFactory(Factory[Config]):
    settings = fields.DictField(
        key_field=fields.StringField(min_chars=3, max_chars=10),
        value_field=fields.TextField("word"),  # All string values
        length=5
    )
```

For truly mixed types, use a custom approach:

```python
class FlexibleConfigFactory(Factory[Config]):
    settings = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)

        # Generate mixed-type dict manually
        instance.settings = {
            "count": fields.IntegerField(min_value=1, max_value=100)(),
            "name": fields.TextField("name")(),
            "active": fields.BooleanField()(),
            "score": fields.FloatField(min_value=0, max_value=100)(),
        }

        return instance
```

## Dynamic Field Selection

### Conditional Fields Based on Context

Choose different field strategies based on test context:

```python
class UserProfileFactory(Factory[UserProfile]):
    name = fields.TextField("name")
    bio = fields.ConstantField(None)

    @classmethod
    def build_complete(cls, **kwargs):
        """Build with all fields populated."""
        return cls.build(
            bio=fields.TextField("paragraph", nb_sentences=3),
            **kwargs
        )

    @classmethod
    def build_minimal(cls, **kwargs):
        """Build with minimal fields."""
        return cls.build(bio=None, **kwargs)

# Usage
complete_profile = UserProfileFactory.build_complete()
assert complete_profile.bio is not None

minimal_profile = UserProfileFactory.build_minimal()
assert minimal_profile.bio is None
```

### Runtime Field Configuration

Configure fields at runtime:

```python
def create_user_factory(age_range: tuple[int, int]):
    """Create a factory with custom age range."""
    min_age, max_age = age_range

    class DynamicUserFactory(Factory[User]):
        name = fields.TextField("name")
        email = fields.TextField("email")
        age = fields.IntegerField(min_value=min_age, max_value=max_age)

    return DynamicUserFactory

# Create specialized factories
teen_factory = create_user_factory((13, 19))
adult_factory = create_user_factory((18, 65))
senior_factory = create_user_factory((60, 100))

teen = teen_factory.build()
assert 13 <= teen.age <= 19

adult = adult_factory.build()
assert 18 <= adult.age <= 65
```

## Advanced Override Patterns

### Partial Object Updates

Update only specific fields while keeping others generated:

```python
class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=18, max_value=65)
    role = fields.ChoiceField(["user", "admin", "moderator"])

def test_role_permissions():
    # Start with random user
    user = UserFactory.build()

    # Override just the role
    admin = UserFactory.build(role="admin")
    moderator = UserFactory.build(role="moderator")

    assert admin.role == "admin"
    assert moderator.role == "moderator"
    # Other fields are still randomized
```

### Cascading Overrides

Override fields that affect other fields:

```python
class PricingFactory(Factory[Pricing]):
    base_price = fields.DecimalField(min_value=10, max_value=100, accuracy=2)
    discount_percent = fields.IntegerField(min_value=0, max_value=50)
    final_price = fields.ConstantField(None)

    @classmethod
    def build(cls, **kwargs):
        instance = super().build(**kwargs)

        # Calculate final price based on other fields
        discount_multiplier = 1 - (instance.discount_percent / 100)
        instance.final_price = instance.base_price * Decimal(discount_multiplier)

        return instance

pricing = PricingFactory.build()
expected = pricing.base_price * (1 - pricing.discount_percent / 100)
assert abs(pricing.final_price - expected) < Decimal("0.01")
```

## Performance Optimization

### Lazy Factory Initialization

Defer expensive factory setup:

```python
class ExpensiveFactory(Factory[Model]):
    # Expensive field generation
    data = fields.TextField("paragraphs", nb=10)

    _cache = {}

    @classmethod
    def build_cached(cls, cache_key: str = "default"):
        if cache_key not in cls._cache:
            cls._cache[cache_key] = cls.build()
        return cls._cache[cache_key]

# Reuse cached instances when appropriate
obj1 = ExpensiveFactory.build_cached()
obj2 = ExpensiveFactory.build_cached()
assert obj1 is obj2  # Same instance
```

**Warning:** Only cache immutable objects or when you don't modify them!

### Batch Generation with Generators

For very large datasets, use generators:

```python
def user_generator(count: int):
    """Generate users lazily."""
    for _ in range(count):
        yield UserFactory.build()

# Process one at a time (memory efficient)
for user in user_generator(10000):
    process(user)
    # Only one user in memory at a time
```

## Testing Strategies

### Property-Based Testing

Combine factorio with property-based testing:

```python
import hypothesis
from hypothesis import given

@given(
    name=hypothesis.strategies.text(min_size=1, max_size=100),
    age=hypothesis.integers(min_value=0, max_value=150),
)
def test_user_properties(name: str, age: int):
    user = UserFactory.build(name=name, age=age)

    # Properties should always hold
    assert user.name == name
    assert user.age == age
    assert isinstance(user.email, str)  # Generated field
```

### Boundary Testing

Test edge cases systematically:

```python
def test_boundary_ages():
    boundary_cases = [0, 1, 17, 18, 64, 65, 150]

    for age in boundary_cases:
        user = UserFactory.build(age=age)
        assert user.age == age

def test_empty_strings():
    user = UserFactory.build(name="", bio="")
    assert user.name == ""
    assert user.bio == ""

def test_maximum_values():
    product = ProductFactory.build(
        price=fields.DecimalField(max_value=Decimal("999999.99"))
    )
    assert product.price <= Decimal("999999.99")
```

### Regression Testing

Save and replay specific test cases:

```python
import json

def test_with_saved_case():
    # Load previously saved test case
    with open("test_cases/user_case_1.json") as f:
        case_data = json.load(f)

    user = UserFactory.build(**case_data)

    # Verify behavior with known inputs
    assert user.is_adult == (user.age >= 18)

def save_test_case(user: User, case_name: str):
    """Save a test case for regression testing."""
    case_data = {
        "name": user.name,
        "age": user.age,
        "email": user.email,
    }
    with open(f"test_cases/{case_name}.json", "w") as f:
        json.dump(case_data, f, indent=2)
```

## Integration Patterns

### Factory Composition

Compose multiple factories for complex scenarios:

```python
class OrderSystem:
    def __init__(self):
        self.user_factory = UserFactory
        self.product_factory = ProductFactory
        self.order_factory = OrderFactory

    def create_complete_order(self):
        user = self.user_factory.build()
        products = [self.product_factory.build() for _ in range(3)]
        order = self.order_factory.build(
            customer=user,
            items=products
        )
        return order

system = OrderSystem()
order = system.create_complete_order()
```

### Factory Registry Pattern

Centralize factory management:

```python
class FactoryRegistry:
    _factories: dict[type, type[Factory]] = {}

    @classmethod
    def register(cls, model: type, factory: type[Factory]):
        cls._factories[model] = factory

    @classmethod
    def get(cls, model: type) -> type[Factory]:
        if model not in cls._factories:
            raise ValueError(f"No factory registered for {model}")
        return cls._factories[model]

    @classmethod
    def build(cls, model: type, **kwargs):
        factory = cls.get(model)
        return factory.build(**kwargs)

# Register factories
FactoryRegistry.register(User, UserFactory)
FactoryRegistry.register(Product, ProductFactory)
FactoryRegistry.register(Order, OrderFactory)

# Build instances
user = FactoryRegistry.build(User, name="John")
product = FactoryRegistry.build(Product, price=29.99)
```

### Mock Integration

Use factories with mocking libraries:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    # Create realistic mock data
    user = UserFactory.build()

    # Mock external service
    with patch("myapp.services.UserService") as mock_service:
        mock_service.get_user.return_value = user

        # Test code that uses the service
        result = my_function_that_uses_service()

        assert result.name == user.name
        mock_service.get_user.assert_called_once()
```

## Debugging Techniques

### Field Inspection

Inspect what fields a factory will generate:

```python
def inspect_factory(factory_class: type[Factory]):
    """Print all fields defined in a factory."""
    print(f"Factory: {factory_class.__name__}")
    print(f"Model: {factory_class.get_model().__name__}")
    print("Fields:")

    for name, value in factory_class.__dict__.items():
        if isinstance(value, AbstractField):
            print(f"  - {name}: {type(value).__name__}")

inspect_factory(UserFactory)
# Output:
# Factory: UserFactory
# Model: User
# Fields:
#   - name: TextField
#   - age: IntegerField
#   - email: TextField
```

### Value Sampling

Sample generated values to verify distributions:

```python
def sample_field(factory_class: type[Factory], field_name: str, samples: int = 100):
    """Sample values from a specific field."""
    values = []
    for _ in range(samples):
        instance = factory_class.build()
        values.append(getattr(instance, field_name))

    print(f"Field: {field_name}")
    print(f"Samples: {samples}")
    print(f"Unique values: {len(set(values))}")
    print(f"Min: {min(values)}")
    print(f"Max: {max(values)}")

    if isinstance(values[0], (int, float)):
        print(f"Average: {sum(values) / len(values):.2f}")

sample_field(UserFactory, "age")
```

### Validation Testing

Ensure generated data passes validation:

```python
def test_all_generated_data_valid():
    """Verify that all generated instances pass validation."""
    errors = []

    for i in range(100):
        try:
            user = UserFactory.build()
            validate_user(user)  # Your validation function
        except Exception as e:
            errors.append((i, str(e)))

    if errors:
        print(f"Found {len(errors)} invalid instances:")
        for idx, error in errors[:10]:  # Show first 10
            print(f"  Instance {idx}: {error}")
        raise AssertionError(f"{len(errors)} instances failed validation")

    print("All 100 instances passed validation ✓")
```

## Anti-Patterns to Avoid

### ❌ Over-Engineering Factories

```python
# ❌ Too complex
class OverengineeredFactory(Factory[Model]):
    field1 = fields.StringField(
        min_chars=5,
        max_chars=10,
        prefix="PRE-",
        suffix="-SUF"
    )

# ✅ Simple and clear
class SimpleFactory(Factory[Model]):
    field1 = fields.TextField("word")
```

### ❌ Hardcoded Test Data in Factories

```python
# ❌ Defeats the purpose
class BadFactory(Factory[User]):
    name = fields.ConstantField("John Doe")
    email = fields.ConstantField("john@example.com")

# ✅ Randomized data
class GoodFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
```

### ❌ Ignoring Type Safety

```python
# ❌ No type hints
class UntypedFactory(Factory):
    name = fields.TextField("name")

# ✅ Properly typed
class TypedFactory(Factory[User]):
    name = fields.TextField("name")
```

### ❌ Circular Dependencies

```python
# ❌ Circular reference
class AFactory(Factory[A]):
    b = fields.FactoryField(BFactory)

class BFactory(Factory[B]):
    a = fields.FactoryField(AFactory)  # Infinite loop!

# ✅ Break the cycle
class AFactory(Factory[A]):
    b_id = fields.IntegerField(min_value=1, max_value=100)

class BFactory(Factory[B]):
    a_id = fields.IntegerField(min_value=1, max_value=100)
```

---

## See Also

- [Field Reference](../api/fields.md) - Complete field documentation
- [Cookbook](../cookbook.md) - Common patterns and recipes
- [Usage Guide](../usage.md) - Basic to intermediate usage
