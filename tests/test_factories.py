from __future__ import annotations

from dataclasses import dataclass

import pytest

from factorio import fields
from factorio.factories import Factory


def test_get_no_model() -> None:
    with pytest.raises(TypeError):
        Factory.get_model()


def test_get_multiple_models() -> None:
    class Spam:
        pass

    class Bacon:
        pass

    class SpamFactory(Factory[Spam]):
        pass

    class BaconFactory(Factory[Bacon]):
        pass

    class SpamAndBaconFactory(SpamFactory, BaconFactory):
        pass

    with pytest.raises(TypeError):
        SpamAndBaconFactory.get_model()


def test_new_style_build() -> None:
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

    class SpamFactory(Factory[Spam]):
        a = fields.IntegerField(max_value=42)
        b = fields.ChoiceField(range(21))
        c = fields.ConstantField(1024)

    class BaconFactory(Factory[Bacon]):
        x = fields.IntegerField(max_value=4)
        y = fields.ListField(fields.StringField(max_chars=4), length=5, variation=2)
        z = fields.FactoryField(SpamFactory)

    spam = SpamFactory.build()
    assert 1 <= spam.a <= 42
    assert 0 <= spam.b <= 20
    assert spam.c == 1024

    plain_bacon = BaconFactory.build()
    assert 0 <= plain_bacon.x <= 4
    assert isinstance(plain_bacon.y, list)
    assert isinstance(plain_bacon.z, Spam)
    assert plain_bacon.t == "Francis"

    bacon = BaconFactory.build(
        x=fields.IntegerField(min_value=99, max_value=101), t="Kevin"
    )
    assert 99 <= bacon.x <= 101
    assert bacon.t == "Kevin"
