# Usage

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

It is possible to override specific fields :

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
