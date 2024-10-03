from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from string import ascii_lowercase, ascii_uppercase, digits

import pytest

from factorio import fields
from factorio.factories import Factory


def test_init_implementation_needed() -> None:
    class MyField(fields.AbstractField[int]):
        pass

    with pytest.raises(NotImplementedError):
        MyField()


def test_call_implementation_needed() -> None:
    class MyField(fields.AbstractField[int]):
        def __init__(self) -> None:
            pass

    with pytest.raises(NotImplementedError):
        MyField()()


def test_boolean_field() -> None:
    assert fields.BooleanField()() in {True, False}


def test_choice_field() -> None:
    choice_field = fields.ChoiceField(range(1, 11))
    assert 1 <= choice_field() <= 10
    # This the choices don't get exhausted
    assert 1 <= choice_field() <= 10


def test_integer_field() -> None:
    assert 1 <= fields.IntegerField(min_value=1, max_value=3)() <= 3


def test_decimal_field() -> None:
    min_value = Decimal("123.123")
    max_value = Decimal("10000.314")
    decimal_field = fields.DecimalField(min_value=min_value, max_value=max_value)
    assert min_value <= decimal_field() <= max_value


def test_float_field() -> None:
    float_field = fields.FloatField(min_value=-100, max_value=100)
    assert abs(float_field()) <= 100


@pytest.mark.parametrize(
    ("include_uppercase", "include_digits", "excepted_alphabet"),
    [
        (False, False, ascii_lowercase),
        (True, False, ascii_lowercase + ascii_uppercase),
        (False, True, ascii_lowercase + digits),
        (True, True, ascii_lowercase + ascii_uppercase + digits),
    ],
)
def test_char_field(
    include_uppercase: bool, include_digits: bool, excepted_alphabet: str
) -> None:
    char_field = fields.CharField(
        include_uppercase=include_uppercase, include_digits=include_digits
    )
    assert char_field() in excepted_alphabet


def test_string_field() -> None:
    string_field = fields.StringField(min_chars=10, max_chars=12, prefix="spam")
    assert 12 <= len(string_field()) <= 16
    assert string_field().startswith("spam")


def test_list_field() -> None:
    list_field = fields.ListField(
        fields.IntegerField(min_value=1, max_value=100), length=5
    )
    assert len(list_field()) == 5
    for item in list_field():
        assert 1 <= item <= 100


def test_tuple_field() -> None:
    tuple_field = fields.TupleField(
        fields.IntegerField(min_value=1, max_value=100), length=5
    )
    assert len(tuple_field()) == 5
    for item in tuple_field():
        assert 1 <= item <= 100


def test_set_field() -> None:
    set_field = fields.SetField(
        fields.IntegerField(min_value=1, max_value=100), length=5
    )
    assert 1 <= len(set_field()) <= 5
    for item in set_field():
        assert 1 <= item <= 100


def test_dict_field() -> None:
    dict_field = fields.DictField(
        key_field=fields.CharField(),
        value_field=fields.IntegerField(min_value=1, max_value=100),
        length=5,
    )
    assert 1 <= len(dict_field()) <= 5
    for key, value in dict_field().items():
        assert isinstance(key, str)
        assert len(key) == 1
        assert 1 <= value <= 100


def test_factory_field() -> None:
    @dataclass
    class Spam:
        a: int

    class SpamFactory(Factory[Spam]):
        class Fields:
            a = fields.IntegerField(max_value=42)

    factory_field = fields.FactoryField(SpamFactory)
    assert 0 <= factory_field().a <= 42
