from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from string import ascii_lowercase, ascii_uppercase, digits
from typing import get_args
from zoneinfo import ZoneInfo

import pytest

from factorio import fields
from factorio.factories import Factory
from factorio.types import TextType


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


def test_date_field() -> None:
    start_date = date(2021, 1, 1)
    end_date = date(2021, 12, 31)
    date_field = fields.DateField(min_date=start_date, max_date=end_date)
    assert start_date <= date_field() <= end_date


def test_time_field() -> None:
    start_time = time(1, 0, 15, 100)
    end_time = time(1, 0, 15, 200)
    time_field = fields.TimeField(min_time=start_time, max_time=end_time)
    assert start_time <= time_field() <= end_time


def test_datetime_field() -> None:
    london_tz = ZoneInfo("Europe/London")
    paris_tz = ZoneInfo("Europe/Paris")
    start_datetime = datetime(2021, 1, 1, 1, 0, 15, 100, tzinfo=london_tz)
    end_datetime = datetime(2021, 12, 31, 1, 0, 15, 200, tzinfo=paris_tz)
    datetime_field = fields.DateTimeField(
        min_datetime=start_datetime, max_datetime=end_datetime
    )
    assert start_datetime <= datetime_field() <= end_datetime
    assert datetime_field().tzinfo == london_tz


def test_naive_datetime_field() -> None:
    start_datetime = datetime(2021, 1, 1, 1, 0, 15, 100)  # noqa: DTZ001
    end_datetime = datetime(2021, 12, 31, 1, 0, 15, 200)  # noqa: DTZ001
    datetime_field = fields.NaiveDateTimeField(
        min_datetime=start_datetime, max_datetime=end_datetime
    )
    assert start_datetime <= datetime_field() <= end_datetime
    assert datetime_field().tzinfo is None


def test_timedelta_field() -> None:
    min_timedelta = timedelta(days=1)
    max_timedelta = timedelta(days=10)
    timedelta_field = fields.TimedeltaField(
        min_timedelta=min_timedelta, max_timedelta=max_timedelta
    )
    assert min_timedelta <= timedelta_field() <= max_timedelta


@pytest.mark.parametrize("areas", [(), ("Etc"), ("Europe", "Antarctica"), ("America",)])
def test_timezone_field(areas: tuple[str, ...]) -> None:
    timezone_field = fields.TimezoneField(areas)
    assert isinstance(timezone_field(), ZoneInfo)


@pytest.mark.parametrize("areas", [("Europe", "Antarctica"), ("America",)])
def test_timezone_field_geographic_areas(areas: tuple[str, ...]) -> None:
    timezone_field = fields.TimezoneField(areas)
    assert isinstance(timezone_field(), ZoneInfo)
    assert timezone_field().key.split("/")[0] in areas


@pytest.mark.parametrize("text_type", get_args(TextType))
def test_text_field(text_type: TextType) -> None:
    string_field = fields.TextField(text_type=text_type)
    assert isinstance(string_field(), str)


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
