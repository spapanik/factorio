=====
Usage
=====

Let's say you have two dataclasses like this:

.. code-block:: python

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


To create a factories for these dataclasses, you can do this:

.. code-block:: python

    class SpamFactory(Factory):
        class Meta:
            model = Spam

        class Fields:
            a = Field("int", max_value=42)
            b = ChoiceField(range(21))
            c = 1024

    class BaconFactory(Factory):
        class Meta:
            model = Bacon

        class Fields:
            x = Field("int", max_value=4)
            y = CollectionField(
                Field("word"), container=list, min_length=3, max_length=7
            )
            z = FactoryField(SpamFactory)

Then using the factories is as simple as:

.. code-block:: python

    bacon = BaconFactory.build()


Contrary to other common factory libraries, `.build()` is needed to create an object.
This is by design, as we feel that it is more explicit and less error prone. `MyModelFactory()`
should only be reserved to create an actual `MyModelFactory` object and never for a `MyModel` object.

Also, another difference with other factory libraries, is that this will never try to save the object
to the database. The reason is that we feel that this is not the responsibility of the factory, and
actually should be done by the test itself.
