from __future__ import annotations

from dataclasses import dataclass

from factorio.factories import Factory
from factorio.fields import ChoiceField, CollectionField, FactoryField, Field


def test_fields():
    @dataclass
    class Spam:
        a: int
        b: int

    @dataclass
    class Bacon:
        x: int
        y: list[str]
        z: Spam

    class SpamFactory(Factory):
        class Meta:
            model = Spam
            fields = {
                "a": Field("int", max_value=42),
                "b": ChoiceField(range(21)),
            }

    class BaconFactory(Factory):
        class Meta:
            model = Bacon
            fields = {
                "x": Field("int", max_value=4),
                "y": CollectionField(
                    Field("word"), container=list, min_length=3, max_length=7
                ),
                "z": FactoryField(SpamFactory),
            }

    spam = SpamFactory.build()
    assert 0 <= spam.b <= 21

    plain_bacon = BaconFactory.build()
    assert 0 <= plain_bacon.x <= 4
    assert isinstance(plain_bacon.y, list)
    assert 0 <= plain_bacon.z.a <= 42

    bacon = BaconFactory.build(x=400)
    assert bacon.x == 400
