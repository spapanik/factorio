# Pydantic Integration

factorio works excellently with Pydantic models, making it easy to generate test data for API testing, validation, and serialization scenarios.

## Basic Setup

### Define Your Models

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    bio: Optional[str] = None

class Post(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    author_id: int
    published: bool = False
    tags: list[str] = []
```

### Create Factories

```python
from factorio import fields
from factorio.factories import Factory

class UserFactory(Factory[User]):
    name = fields.StringField(min_chars=3, max_chars=50)
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=18, max_value=65)
    bio = fields.TextField("paragraph", nb_sentences=2)
    # Don't set id or created_at - let Pydantic handle defaults

class PostFactory(Factory[Post]):
    title = fields.TextField("sentence", nb_words=5)
    content = fields.TextField("paragraphs", nb=2)
    author_id = fields.IntegerField(min_value=1, max_value=1000)
    published = fields.BooleanField(truth_probability=70)
    tags = fields.ListField(fields.TextField("word"), length=3)
```

## Usage in Tests

### Building Valid Models

```python
def test_user_creation():
    user = UserFactory.build()

    # Pydantic validation happens automatically
    assert isinstance(user, User)
    assert user.name
    assert "@" in user.email
    assert 18 <= user.age <= 65

    # Model methods work as expected
    user_dict = user.model_dump()
    assert "name" in user_dict
    assert "email" in user_dict
```

### Testing Validation

```python
def test_invalid_age_rejected():
    # Override with invalid age
    try:
        user = UserFactory.build(age=200)
        # If we get here, validation didn't catch it
        assert False, "Should have raised ValidationError"
    except Exception as e:
        # Pydantic validation error
        assert "age" in str(e).lower()
```

### JSON Serialization

```python
import json

def test_user_serialization():
    user = UserFactory.build()

    # Serialize to JSON
    user_json = user.model_dump_json()
    parsed = json.loads(user_json)

    assert parsed["name"] == user.name
    assert parsed["email"] == user.email
    assert isinstance(parsed["created_at"], str)  # ISO format
```

## Advanced Patterns

### Nested Pydantic Models

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str
    zipcode: str

class UserWithAddress(BaseModel):
    name: str
    email: EmailStr
    address: Address
    secondary_addresses: List[Address] = []

class AddressFactory(Factory[Address]):
    street = fields.TextField("street_address")
    city = fields.TextField("city")
    country = fields.TextField("country")
    zipcode = fields.TextField("postcode")

class UserWithAddressFactory(Factory[UserWithAddress]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    address = fields.FactoryField(AddressFactory)
    secondary_addresses = fields.ListField(
        fields.FactoryField(AddressFactory),
        length=2
    )

def test_nested_models():
    user = UserWithAddressFactory.build()

    assert isinstance(user.address, Address)
    assert user.address.city
    assert len(user.secondary_addresses) == 2
    assert all(isinstance(addr, Address) for addr in user.secondary_addresses)
```

### Optional Fields

```python
class Profile(BaseModel):
    username: str
    website: Optional[str] = None
    twitter: Optional[str] = None

class ProfileFactory(Factory[Profile]):
    username = fields.TextField("user_name")
    # Sometimes include optional fields
    website = fields.TextField("url")  # Will always generate
    twitter = fields.ConstantField(None)  # Always None

def test_optional_fields():
    profile = ProfileFactory.build()
    assert profile.username
    assert profile.website  # Has value
    assert profile.twitter is None  # Explicitly None
```

### Using Field Defaults

```python
class Settings(BaseModel):
    theme: str = "light"
    notifications: bool = True
    language: str = "en"

class SettingsFactory(Factory[Settings]):
    # Override some defaults, keep others
    theme = fields.ChoiceField(["light", "dark", "system"])
    # Don't define notifications or language - use model defaults

def test_partial_override():
    settings = SettingsFactory.build()
    assert settings.theme in ["light", "dark", "system"]
    assert settings.notifications is True  # Default
    assert settings.language == "en"  # Default
```

## API Testing

### FastAPI Integration

```python
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()

@app.post("/users")
def create_user(user: User):
    return {"message": f"User {user.name} created", "id": 123}

client = TestClient(app)

def test_create_user_endpoint():
    user = UserFactory.build()

    response = client.post("/users", json=user.model_dump())

    assert response.status_code == 200
    assert "created" in response.json()["message"]
```

### Testing Request Validation

```python
def test_invalid_email_rejected():
    # Build valid user first
    user = UserFactory.build()

    # Manually set invalid email
    user.email = "not-an-email"

    response = client.post("/users", json=user.model_dump())

    # FastAPI/Pydantic should reject this
    assert response.status_code == 422
    assert "email" in str(response.json())
```

## Complete Example

```python
from pydantic import BaseModel, Field, EmailStr, validator
from factorio import fields
from factorio.factories import Factory

# Model with validation
class Product(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    category: str
    in_stock: bool = True
    tags: list[str] = []

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Too many tags')
        return v

# Factory
class ProductFactory(Factory[Product]):
    name = fields.StringField(min_chars=3, max_chars=50)
    price = fields.FloatField(min_value=0.01, max_value=999.99)
    category = fields.ChoiceField(["electronics", "books", "clothing"])
    in_stock = fields.BooleanField(truth_probability=80)
    tags = fields.ListField(fields.TextField("word"), length=3, variation=2)

# Tests
def test_valid_product():
    product = ProductFactory.build()

    assert product.name
    assert product.price > 0
    assert product.category in ["electronics", "books", "clothing"]
    assert len(product.tags) <= 10  # Validator constraint

def test_product_json():
    product = ProductFactory.build()

    # For API responses
    json_data = product.model_dump()
    assert "name" in json_data
    assert "price" in json_data

    # Exclude None values
    compact = product.model_dump(exclude_none=True)
    assert compact == json_data  # No None values in this case

def test_bulk_products():
    products = [ProductFactory.build() for _ in range(5)]

    # All valid
    assert all(p.price > 0 for p in products)
    assert all(p.name for p in products)

    # Convert to list for API
    products_data = [p.model_dump() for p in products]
    assert len(products_data) == 5
```

## Best Practices

### Use Realistic Data for API Tests

```python
class APIUserFactory(Factory[User]):
    # Generate realistic data that matches production patterns
    name = fields.TextField("name")  # Real names
    email = fields.TextField("safe_email")  # Safe emails
    age = fields.IntegerField(min_value=18, max_value=80)  # Realistic ages
    bio = fields.TextField("paragraph", nb_sentences=3)  # Realistic bios

def test_api_with_realistic_data(client: TestClient):
    user = APIUserFactory.build()

    response = client.post("/users", json=user.model_dump())
    assert response.status_code == 201

    # The realistic data helps catch edge cases
    assert len(user.name) <= 100  # Field constraint
    assert "@" in user.email  # Email format
```

### Test Edge Cases

```python
def test_minimum_age():
    user = UserFactory.build(age=0)  # Edge case
    assert user.age == 0

def test_maximum_age():
    user = UserFactory.build(age=150)  # Edge case
    assert user.age == 150

def test_empty_bio():
    user = UserFactory.build(bio="")  # Empty string
    assert user.bio == ""
```

### Type Safety

```python
# factorio's type hints work well with Pydantic
def process_user(user: User) -> str:
    return f"{user.name} <{user.email}>"

def test_type_safety():
    user = UserFactory.build()

    # Type checker knows this is a User
    result = process_user(user)
    assert isinstance(result, str)
```

## Common Pitfalls

### ⚠️ Don't Duplicate Validation

```python
# ❌ Wrong - factory generates invalid data
class BadUserFactory(Factory[User]):
    age = fields.IntegerField(min_value=-100, max_value=200)  # Outside Pydantic constraints!

# ✅ Correct - respect model constraints
class GoodUserFactory(Factory[User]):
    age = fields.IntegerField(min_value=0, max_value=150)  # Matches Field(ge=0, le=150)
```

### ⚠️ Handle Required Fields

```python
# ❌ Missing required field
class IncompleteUserFactory(Factory[User]):
    email = fields.TextField("email")
    # Forgot name!

# ✅ Include all required fields
class CompleteUserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
```

### ⚠️ Be Careful with Defaults

```python
class Config(BaseModel):
    timeout: int = 30
    retries: int = 3

# ❌ Overriding when you want defaults
class ConfigFactory(Factory[Config]):
    timeout = fields.IntegerField(min_value=1, max_value=100)
    retries = fields.IntegerField(min_value=1, max_value=10)

# ✅ Let Pydantic handle defaults when appropriate
class SmartConfigFactory(Factory[Config]):
    # Only override what you need to test
    timeout = fields.IntegerField(min_value=1, max_value=100)
    # retries uses model default (3)
```
