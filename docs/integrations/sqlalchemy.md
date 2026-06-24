# SQLAlchemy Integration

factorio works seamlessly with SQLAlchemy models. Since factorio doesn't interact with databases, you maintain full control over when and how objects are persisted.

## Basic Setup

### Define Your Models

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

Base = DeclarativeBase()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationship
    author = relationship("User", back_populates="posts")
```

### Create Factories

```python
from factorio import fields
from factorio.factories import Factory

class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=18, max_value=65)
    # Don't set created_at - let SQLAlchemy handle defaults

class PostFactory(Factory[Post]):
    title = fields.TextField("sentence", nb_words=6)
    content = fields.TextField("paragraphs", nb=3)
    author = fields.FactoryField(UserFactory)
```

## Usage in Tests

### Creating Objects Without Persistence

```python
def test_user_creation():
    # Build object in memory (no database interaction)
    user = UserFactory.build()

    assert isinstance(user, User)
    assert user.name is not None
    assert "@" in user.email
    assert 18 <= user.age <= 65
```

### Persisting to Database

```python
from sqlalchemy.orm import Session

def test_save_user_to_database(db_session: Session):
    # Build object
    user = UserFactory.build()

    # Explicitly save to database
    db_session.add(user)
    db_session.commit()

    # Verify it was saved
    assert user.id is not None
    saved_user = db_session.query(User).filter_by(email=user.email).first()
    assert saved_user is not None
    assert saved_user.name == user.name
```

### Working with Relationships

```python
def test_post_with_author(db_session: Session):
    # Build post (automatically builds author too)
    post = PostFactory.build()

    assert isinstance(post.author, User)
    assert post.author.name is not None

    # Save both to database
    db_session.add(post)
    db_session.commit()

    # Verify relationship
    assert post.author_id is not None
    assert post.author.id == post.author_id
```

## Advanced Patterns

### Overriding Foreign Keys

When you need specific relationships:

```python
def test_post_with_existing_author(db_session: Session):
    # Create and save an author first
    existing_user = UserFactory.build()
    db_session.add(existing_user)
    db_session.commit()

    # Create post with existing author
    post = PostFactory.build(author=existing_user)
    db_session.add(post)
    db_session.commit()

    assert post.author_id == existing_user.id
```

### Bulk Creation

```python
def test_create_multiple_users(db_session: Session):
    # Create multiple users
    users = [UserFactory.build() for _ in range(10)]

    # Bulk insert
    db_session.add_all(users)
    db_session.commit()

    assert len(users) == 10
    assert all(user.id is not None for user in users)
```

### Custom Field Ranges per Test

```python
def test_adult_users(db_session: Session):
    # Override age range for this specific test
    adult_user = UserFactory.build(
        age=fields.IntegerField(min_value=21, max_value=65)
    )
    db_session.add(adult_user)
    db_session.commit()

    assert adult_user.age >= 21

def test_teen_users(db_session: Session):
    # Different age range
    teen_user = UserFactory.build(
        age=fields.IntegerField(min_value=18, max_value=20)
    )
    db_session.add(teen_user)
    db_session.commit()

    assert 18 <= teen_user.age <= 20
```

## Testing Best Practices

### Use Fixtures for Database Sessions

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.rollback()
    session.close()
```

### Clean State Between Tests

```python
@pytest.fixture(autouse=True)
def clean_db(db_session):
    """Automatically rollback after each test."""
    yield
    db_session.rollback()
```

### Factory Helpers for Common Patterns

```python
class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
    age = fields.IntegerField(min_value=18, max_value=65)

    @classmethod
    def create_and_save(cls, session: Session, **kwargs) -> User:
        """Helper to build and save in one step."""
        user = cls.build(**kwargs)
        session.add(user)
        session.commit()
        return user

# Usage in tests
def test_quick_user_creation(db_session: Session):
    user = UserFactory.create_and_save(db_session, age=25)
    assert user.id is not None
    assert user.age == 25
```

## Common Pitfalls

### ⚠️ Don't Set Primary Keys in Factories

```python
# ❌ Wrong - let the database assign IDs
class UserFactory(Factory[User]):
    id = fields.IntegerField()  # Don't do this!
    name = fields.TextField("name")

# ✅ Correct - only set non-PK fields
class UserFactory(Factory[User]):
    name = fields.TextField("name")
    email = fields.TextField("email")
```

### ⚠️ Handle Unique Constraints

```python
# ❌ May cause integrity errors
user1 = UserFactory.build()
user2 = UserFactory.build()
# Both might have same email!

# ✅ Override to ensure uniqueness
user1 = UserFactory.build(email="user1@example.com")
user2 = UserFactory.build(email="user2@example.com")

# Or use sequences (see Cookbook)
```

### ⚠️ Don't Forget to Commit

```python
# ❌ Object won't be persisted
user = UserFactory.build()
db_session.add(user)
# Forgot to commit!

# ✅ Always commit after adding
user = UserFactory.build()
db_session.add(user)
db_session.commit()
```

## Complete Example

```python
import pytest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from factorio import fields
from factorio.factories import Factory

# Models
Base = DeclarativeBase()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer)  # Price in cents
    category = Column(String(50))

# Factory
class ProductFactory(Factory[Product]):
    name = fields.TextField("word").capitalize()
    price = fields.IntegerField(min_value=100, max_value=99999)
    category = fields.ChoiceField(["electronics", "books", "clothing"])

# Test
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_product_workflow(db_session):
    # Build product
    product = ProductFactory.build()
    assert isinstance(product, Product)
    assert product.name
    assert 100 <= product.price <= 99999

    # Save to database
    db_session.add(product)
    db_session.commit()
    assert product.id is not None

    # Query back
    saved = db_session.query(Product).get(product.id)
    assert saved.name == product.name
    assert saved.price == product.price
```
