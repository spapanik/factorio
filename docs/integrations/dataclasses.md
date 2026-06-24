# Dataclasses Integration

factorio was designed with dataclasses in mind. This is the most straightforward integration since dataclasses are simple Python objects with no external dependencies.

## Basic Setup

### Define Your Dataclasses

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User:
    name: str
    email: str
    age: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    bio: Optional[str] = None

@dataclass
class Address:
    street: str
    city: str
    country: str
    zipcode: str

@dataclass
class UserWithAddress:
    name: str
    email: str
    address: Address
```

### Create Factories

```python
from factorio import fields
from factorio.factories import Factory

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=18, max_value=65)
    bio = fields.TextField("paragraph", nb_sentences=2)

class AddressFactory(Factory[Address]):
    street = fields.TextField("street_address")
    city = fields.TextField("city")
    country = fields.TextField("country")
    zipcode = fields.TextField("postcode")

class UserWithAddressFactory(Factory[UserWithAddress]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    address = fields.FactoryField(AddressFactory)
```

## Usage Examples

### Simple Object Creation

```python
def test_basic_user():
    user = UserFactory.build()

    assert isinstance(user, User)
    assert user.name
    assert "@" in user.email
    assert 18 <= user.age <= 65
    assert isinstance(user.created_at, datetime)
```

### Nested Objects

```python
def test_user_with_address():
    user = UserWithAddressFactory.build()

    assert isinstance(user, UserWithAddress)
    assert isinstance(user.address, Address)
    assert user.address.city
    assert user.address.country
```

### Field Overrides

```python
def test_custom_user():
    user = UserFactory.build(
        name="John Doe",
        age=30,
        email="john@example.com"
    )

    assert user.name == "John Doe"
    assert user.age == 30
    assert user.email == "john@example.com"
```

## Advanced Patterns

### Default Values

Dataclasses support default values, which work seamlessly with factorio:

```python
@dataclass
class Product:
    name: str
    price: float
    in_stock: bool = True
    quantity: int = 0
    tags: list[str] = field(default_factory=list)

class ProductFactory(Factory[Product]):
    name = fields.TextField("word").capitalize()
    price = fields.FloatField(min_value=0.01, max_value=999.99)
    # Don't define in_stock, quantity, or tags - use defaults

def test_defaults_preserved():
    product = ProductFactory.build()

    assert product.in_stock is True  # Default
    assert product.quantity == 0  # Default
    assert product.tags == []  # Default from factory
```

**Note:** If you want to override a field that has a default, just define it in the factory:

```python
class CustomProductFactory(Factory[Product]):
    name = fields.TextField("word")
    price = fields.FloatField(min_value=1, max_value=100)
    in_stock = fields.BooleanField(truth_probability=80)  # Override default
    quantity = fields.IntegerField(min_value=0, max_value=100)  # Override default
```

### Mutable Default Arguments

Be careful with mutable defaults in dataclasses:

```python
@dataclass
class ShoppingCart:
    items: list[str] = field(default_factory=list)  # ✅ Correct
    # items: list[str] = []  # ❌ Wrong - shared mutable default!

class ShoppingCartFactory(Factory[ShoppingCart]):
    items = fields.ListField(fields.TextField("word"), length=3)

def test_separate_instances():
    cart1 = ShoppingCartFactory.build()
    cart2 = ShoppingCartFactory.build()

    # Each cart has its own items list
    assert cart1.items is not cart2.items
    cart1.items.append("extra")
    assert len(cart1.items) == 4
    assert len(cart2.items) == 3
```

### Post-Initialization Processing

Use `__post_init__` for validation or computed fields:

```python
@dataclass
class Circle:
    radius: float

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError("Radius cannot be negative")
        self.area = 3.14159 * self.radius ** 2

class CircleFactory(Factory[Circle]):
    radius = fields.FloatField(min_value=0.1, max_value=100.0)

def test_circle_validation():
    circle = CircleFactory.build()

    assert circle.radius > 0
    assert hasattr(circle, 'area')
    assert circle.area > 0

def test_invalid_radius_rejected():
    try:
        circle = CircleFactory.build(radius=-5)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "negative" in str(e).lower()
```

### Inheritance

Dataclasses support inheritance, and so do factories:

```python
@dataclass
class Vehicle:
    make: str
    model: str
    year: int

@dataclass
class Car(Vehicle):
    num_doors: int
    fuel_type: str

@dataclass
class ElectricCar(Car):
    battery_capacity: float  # kWh
    charging_time: float  # hours

class VehicleFactory(Factory[Vehicle]):
    make = fields.ChoiceField(["Toyota", "Honda", "Ford"])
    model = fields.TextField("word").capitalize()
    year = fields.IntegerField(min_value=2000, max_value=2024)

class CarFactory(VehicleFactory):
    num_doors = fields.ChoiceField([2, 4])
    fuel_type = fields.ChoiceField(["gasoline", "diesel", "hybrid"])

class ElectricCarFactory(CarFactory):
    battery_capacity = fields.FloatField(min_value=40.0, max_value=100.0)
    charging_time = fields.FloatField(min_value=0.5, max_value=8.0)
    fuel_type = fields.ConstantField("electric")  # Override parent

def test_inheritance():
    car = CarFactory.build()
    assert isinstance(car, Car)
    assert car.num_doors in [2, 4]

    electric = ElectricCarFactory.build()
    assert isinstance(electric, ElectricCar)
    assert electric.fuel_type == "electric"
    assert 40.0 <= electric.battery_capacity <= 100.0
```

## Testing Patterns

### Comparison and Equality

```python
@dataclass
class Point:
    x: float
    y: float

class PointFactory(Factory[Point]):
    x = fields.FloatField(min_value=-100, max_value=100)
    y = fields.FloatField(min_value=-100, max_value=100)

def test_point_equality():
    p1 = PointFactory.build(x=10.0, y=20.0)
    p2 = PointFactory.build(x=10.0, y=20.0)
    p3 = PointFactory.build(x=15.0, y=20.0)

    assert p1 == p2  # Same values
    assert p1 != p3  # Different x
```

### Sorting

```python
@dataclass(order=True)
class Student:
    grade: int
    name: str

class StudentFactory(Factory[Student]):
    grade = fields.IntegerField(min_value=1, max_value=12)
    name = fields.TextField("name")

def test_student_sorting():
    students = [StudentFactory.build() for _ in range(10)]

    # Sort by grade (primary), then name (secondary)
    sorted_students = sorted(students)

    assert sorted_students[0].grade <= sorted_students[-1].grade
```

### Conversion to Dict/Tuple

```python
from dataclasses import asdict, astuple

def test_conversion():
    user = UserFactory.build()

    # Convert to dict
    user_dict = asdict(user)
    assert isinstance(user_dict, dict)
    assert user_dict["name"] == user.name

    # Convert to tuple
    user_tuple = astuple(user)
    assert isinstance(user_tuple, tuple)
    assert user_tuple[0] == user.name  # First field
```

## Complete Example

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from factorio import fields
from factorio.factories import Factory

# Domain models
@dataclass
class Book:
    title: str
    author: str
    isbn: str
    published_date: date
    pages: int
    genre: str
    description: Optional[str] = None

@dataclass
class LibraryMember:
    name: str
    email: str
    member_since: date
    borrowed_books: list[str] = field(default_factory=list)
    max_books: int = 5

@dataclass
class Loan:
    book_isbn: str
    member_email: str
    loan_date: date
    due_date: date
    returned: bool = False

# Factories
class BookFactory(Factory[Book]):
    title = fields.TextField("sentence", nb_words=4)
    author = fields.TextField("name")
    isbn = fields.TextField("isbn13")
    published_date = fields.DateField(
        min_date=date(1900, 1, 1),
        max_date=date(2024, 12, 31)
    )
    pages = fields.IntegerField(min_value=50, max_value=1000)
    genre = fields.ChoiceField([
        "fiction", "non-fiction", "mystery", "sci-fi", "romance"
    ])
    description = fields.TextField("paragraph", nb_sentences=2)

class LibraryMemberFactory(Factory[LibraryMember]):
    name = fields.TextField("name")
    email = fields.TextField("safe_email")
    member_since = fields.DateField(
        min_date=date(2020, 1, 1),
        max_date=date(2024, 12, 31)
    )
    borrowed_books = fields.ListField(
        fields.TextField("isbn13"),
        length=2,
        variation=1
    )
    max_books = fields.IntegerField(min_value=3, max_value=10)

class LoanFactory(Factory[Loan]):
    book_isbn = fields.TextField("isbn13")
    member_email = fields.TextField("safe_email")
    loan_date = fields.DateField()
    due_date = fields.DateField()  # Should be after loan_date
    returned = fields.BooleanField(truth_probability=60)

# Tests
def test_book_creation():
    book = BookFactory.build()

    assert book.title
    assert book.author
    assert len(book.isbn) == 13  # ISBN-13 format
    assert 50 <= book.pages <= 1000
    assert book.genre in ["fiction", "non-fiction", "mystery", "sci-fi", "romance"]

def test_member_with_books():
    member = LibraryMemberFactory.build()

    assert member.name
    assert "@" in member.email
    assert 1 <= len(member.borrowed_books) <= 3
    assert all(isinstance(isbn, str) for isbn in member.borrowed_books)

def test_loan_workflow():
    loan = LoanFactory.build()

    assert loan.book_isbn
    assert "@" in loan.member_email
    assert loan.due_date >= loan.loan_date  # Due date after loan date
    assert isinstance(loan.returned, bool)

def test_bulk_operations():
    books = [BookFactory.build() for _ in range(20)]

    # All books are valid
    assert all(book.title for book in books)
    assert all(book.pages > 0 for book in books)

    # Unique titles (likely, but not guaranteed)
    titles = [book.title for book in books]
    unique_titles = set(titles)
    # With 20 books, we probably have some duplicates
    assert len(unique_titles) >= 10  # At least half are unique
```

## Best Practices

### Use Type Hints

```python
# ✅ Good - clear types
@dataclass
class User:
    name: str
    age: int
    email: str

# ❌ Avoid - missing type hints
@dataclass
class BadUser:
    name: Any  # Too vague
    age = None  # No type annotation
```

### Validate in `__post_init__`

```python
@dataclass
class Temperature:
    celsius: float

    def __post_init__(self):
        if self.celsius < -273.15:
            raise ValueError("Below absolute zero!")

class TemperatureFactory(Factory[Temperature]):
    celsius = fields.FloatField(min_value=-100, max_value=100)

# Factory respects validation
temp = TemperatureFactory.build()
assert temp.celsius >= -273.15
```

### Keep Factories Simple

```python
# ✅ Simple factory
class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")

# ❌ Overly complex
class ComplicatedUserFactory(Factory[User]):
    name = fields.StringField(
        min_chars=5,
        max_chars=20,
        prefix="USR-"
    )
    email = fields.StringField(
        min_chars=10,
        max_chars=30,
        suffix="@test.local"
    )
    # Just use TextField for realistic data!
```

### Document Field Choices

```python
class ProductFactory(Factory[Product]):
    # Price in cents to avoid floating point issues
    price_cents = fields.IntegerField(min_value=100, max_value=99999)

    # Categories match our database enum
    category = fields.ChoiceField([
        "electronics",
        "books",
        "clothing",
        "home_garden"
    ])
```

## Common Pitfalls

### ⚠️ Frozen Dataclasses

```python
@dataclass(frozen=True)
class ImmutablePoint:
    x: float
    y: float

class PointFactory(Factory[ImmutablePoint]):
    x = fields.FloatField()
    y = fields.FloatField()

def test_frozen():
    point = PointFactory.build()

    # Can't modify frozen dataclass
    try:
        point.x = 10.0
        assert False, "Should raise FrozenInstanceError"
    except Exception:
        pass  # Expected
```

### ⚠️ Missing Required Fields

```python
@dataclass
class Person:
    name: str  # Required
    age: int   # Required

# ❌ Missing required field in factory
class BadPersonFactory(Factory[Person]):
    name = fields.TextField("name")
    # Forgot age!

# ✅ Include all required fields
class GoodPersonFactory(Factory[Person]):
    name = fields.TextField("name")
    age = fields.IntegerField(min_value=0, max_value=120)
```

### ⚠️ Shared Mutable State

```python
@dataclass
class Team:
    members: list[str] = field(default_factory=list)  # ✅ Correct

# ❌ Wrong - don't do this in dataclasses
# members: list[str] = []

def test_no_shared_state():
    team1 = TeamFactory.build()
    team2 = TeamFactory.build()

    team1.members.append("Alice")
    assert "Alice" not in team2.members  # Separate lists
```
