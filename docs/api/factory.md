# Factory API Reference

The `Factory` class is the core component of factorio. It provides the mechanism for generating model instances with realistic data.

## Factory[T]

A generic base class that all factories must inherit from. The type parameter `T` specifies the model type that this factory creates.

### Type Parameter

- `T`: The model type (dataclass, Pydantic model, SQLAlchemy model, etc.)

### Class Methods

#### get_model() → type[T]

Extracts the model type from the factory's generic type annotation.

**Returns:** The concrete model type that this factory creates.

**Raises:**
- `TypeError` - If no concrete model is found
- `TypeError` - If multiple concrete models are found (ambiguous inheritance)

**Example:**
```python
from factorio.factories import Factory
from dataclasses import dataclass

@dataclass
class User:
    name: str

class UserFactory(Factory[User]):
    name = fields.TextField("name")

model_type = UserFactory.get_model()
assert model_type is User
```

**How it works:**
The method inspects the Method Resolution Order (MRO) of the factory class and extracts type arguments from `__orig_bases__`. It looks for non-TypeVar types in the generic parameters.

**Note:** This is called automatically by `.build()`, so you rarely need to call it directly.

---

#### build(**kwargs) → T

Creates an instance of the model with generated field values.

**Parameters:**
- `**kwargs`: Optional field overrides. Can be:
  - Direct values (e.g., `name="John"`)
  - Field instances (e.g., `age=fields.IntegerField(min_value=20, max_value=30)`)

**Returns:** An instance of type `T` (the model)

**Example:**
```python
from factorio import fields
from factorio.factories import Factory

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    age = fields.IntegerField(min_value=18, max_value=65)
    email = fields.TextField("email")

# Basic usage
user = UserFactory.build()
assert isinstance(user, User)
assert user.name
assert 18 <= user.age <= 65

# Override with values
user = UserFactory.build(name="Jane", age=30)
assert user.name == "Jane"
assert user.age == 30

# Override with field instances
user = UserFactory.build(
    age=fields.IntegerField(min_value=50, max_value=60)
)
assert 50 <= user.age <= 60
```

**How it works:**
1. Calls `get_model()` to determine the model type
2. Iterates through class attributes to find `AbstractField` instances
3. Calls each field to generate a value
4. Applies any kwargs overrides (values or field instances)
5. Instantiates the model with all field values
6. Returns the model instance

**Important:**
- Fields are evaluated when `.build()` is called, not when the factory is defined
- Override values take precedence over factory-defined fields
- If you pass a field instance as an override, it will be evaluated

---

### Creating Factories

#### Basic Factory

```python
from dataclasses import dataclass
from factorio import fields
from factorio.factories import Factory

@dataclass
class Product:
    name: str
    price: float
    in_stock: bool

class ProductFactory(Factory[Product]):
    name = fields.TextField("word").capitalize()
    price = fields.FloatField(min_value=0.01, max_value=999.99)
    in_stock = fields.BooleanField(truth_probability=80)

product = ProductFactory.build()
```

#### Factory with Nested Objects

```python
@dataclass
class Address:
    street: str
    city: str

@dataclass
class User:
    name: str
    address: Address

class AddressFactory(Factory[Address]):
    street = fields.TextField("street_address")
    city = fields.TextField("city")

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    address = fields.FactoryField(AddressFactory)

user = UserFactory.build()
assert isinstance(user.address, Address)
```

#### Factory Inheritance

```python
class BaseUserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")

class AdminUserFactory(BaseUserFactory):
    role = fields.ConstantField("admin")
    is_admin = fields.ConstantField(True)

class RegularUserFactory(BaseUserFactory):
    role = fields.ChoiceField(["user", "member"])
    is_admin = fields.ConstantField(False)

admin = AdminUserFactory.build()
assert admin.role == "admin"
assert admin.is_admin is True
```

---

### Common Patterns

#### Minimal Factory

Only define fields you want to customize:

```python
@dataclass
class Config:
    timeout: int = 30
    retries: int = 3
    debug: bool = False

class ConfigFactory(Factory[Config]):
    # Only override timeout, use defaults for others
    timeout = fields.IntegerField(min_value=1, max_value=120)

config = ConfigFactory.build()
assert config.retries == 3  # Default
assert config.debug is False  # Default
```

#### Factory with All Fields

Define all fields explicitly:

```python
class CompleteUserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=18, max_value=65)
    bio = fields.TextField("paragraph", nb_sentences=2)
    is_active = fields.BooleanField(truth_probability=90)
    created_at = fields.DateTimeField()
```

#### Reusable Factory Base

Create mixins for common functionality:

```python
class TimestampedFactory(Factory[T]):
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()

class AuditableFactory(Factory[T]):
    created_by = fields.TextField("user_name")
    updated_by = fields.TextField("user_name")

class ArticleFactory(TimestampedFactory, AuditableFactory):
    title = fields.TextField("sentence")
    content = fields.TextField("paragraphs", nb=3)

article = ArticleFactory.build()
assert hasattr(article, 'created_at')
assert hasattr(article, 'created_by')
```

---

### Error Handling

#### No Model Found

```python
class BadFactory(Factory):  # Missing type parameter
    name = fields.TextField("name")

try:
    BadFactory.get_model()
except TypeError as e:
    print(e)  # "No concrete model found for BadFactory"
```

**Fix:** Always specify the type parameter:
```python
class GoodFactory(Factory[User]):
    name = fields.TextField("name")
```

#### Multiple Models Found

```python
class UserFactory1(Factory[User]):
    pass

class UserFactory2(Factory[User]):
    pass

# Ambiguous inheritance
class ConfusedFactory(UserFactory1, UserFactory2):
    pass

try:
    ConfusedFactory.get_model()
except TypeError as e:
    print(e)  # "Multiple concrete models found for ConfusedFactory"
```

**Fix:** Avoid multiple inheritance from different typed factories, or ensure they share the same model type.

---

### Best Practices

#### DO:

✅ Always specify the type parameter: `Factory[MyModel]`
✅ Use descriptive factory names: `UserFactory`, not `UF`
✅ Keep factories focused on one model
✅ Override fields in tests when needed
✅ Use factory inheritance for common patterns

#### DON'T:

❌ Call `Factory()` without `.build()` (creates factory instance, not model)
❌ Define fields that aren't in the model
❌ Create circular factory dependencies
❌ Hardcode values that should be randomized
❌ Forget that fields are evaluated at build time

---

### Advanced Usage

#### Dynamic Factory Creation

```python
def create_factory_for_model(model_class: type[T]) -> type[Factory[T]]:
    """Dynamically create a factory for any model."""

    class DynamicFactory(Factory[model_class]):
        pass

    return DynamicFactory

UserFactory = create_factory_for_model(User)
user = UserFactory.build()
```

#### Factory Registration Pattern

```python
FACTORY_REGISTRY: dict[type, type[Factory]] = {}

def register_factory(model_class: type[T], factory_class: type[Factory[T]]):
    FACTORY_REGISTRY[model_class] = factory_class

def build_instance(model_class: type[T], **kwargs) -> T:
    factory = FACTORY_REGISTRY.get(model_class)
    if not factory:
        raise ValueError(f"No factory registered for {model_class}")
    return factory.build(**kwargs)

# Register factories
register_factory(User, UserFactory)
register_factory(Product, ProductFactory)

# Build instances
user = build_instance(User, name="John")
product = build_instance(Product, price=29.99)
```

#### Custom Build Logic

Override `.build()` for custom behavior:

```python
class ValidatedUserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=0, max_value=150)

    @classmethod
    def build(cls, **kwargs) -> User:
        instance = super().build(**kwargs)

        # Post-build validation
        if instance.age < 18:
            instance.is_minor = True
        else:
            instance.is_minor = False

        return instance

user = ValidatedUserFactory.build(age=15)
assert user.is_minor is True
```

---

### Performance Tips

1. **Reuse factory classes** - Don't recreate factories in loops
2. **Minimize nested factories** - Each `FactoryField` creates a full object graph
3. **Use ConstantField for static values** - Faster than generating random data
4. **Batch operations** - Generate lists with list comprehensions

```python
# ✅ Fast
users = [UserFactory.build() for _ in range(100)]

# ❌ Slower
users = []
for _ in range(100):
    users.append(UserFactory.build())
```

---

### See Also

- [Field Reference](fields.md) - All available field types
- [Usage Guide](../usage.md) - Comprehensive usage examples
- [Cookbook](../cookbook.md) - Common patterns and recipes
