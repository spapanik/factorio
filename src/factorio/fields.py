from __future__ import annotations

import string
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from secrets import choice
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast
from zoneinfo import ZoneInfo

from faker import Faker
from pyutilkit.date_utils import get_timezones

if TYPE_CHECKING:
    from collections.abc import Iterable

    from factorio.enums import TextType, UnstableTextType
    from factorio.factories import Factory

_fake = Faker()

K = TypeVar("K")
T = TypeVar("T")
UTC = ZoneInfo("UTC")


class AbstractField(Generic[T]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    def __call__(self) -> T:
        raise NotImplementedError


class ChoiceField(AbstractField[T]):
    def __init__(self, options: Iterable[T]) -> None:
        self.options = list(options)

    def __call__(self) -> T:
        return choice(self.options)


class BooleanField(AbstractField[int]):
    def __init__(self, truth_probability: int = 50) -> None:
        self.truth_probability = truth_probability

    def __call__(self) -> int:
        return _fake.pybool(truth_probability=self.truth_probability)


class IntegerField(AbstractField[int]):
    def __init__(
        self, min_value: int = 1, max_value: int = 9999, step: int = 1
    ) -> None:
        self.min_value = min_value
        self.max_value = max_value
        self.step = step

    def __call__(self) -> int:
        return _fake.pyint(
            min_value=self.min_value, max_value=self.max_value, step=self.step
        )


class DecimalField(AbstractField[Decimal]):
    def __init__(
        self,
        min_value: float | Decimal = 0,
        max_value: float | Decimal = 9999,
        accuracy: int = 3,
        variation: int = 0,
    ) -> None:
        self.min_value = Decimal(min_value)
        self.max_value = Decimal(max_value)
        self.min_length = accuracy - variation
        self.max_length = accuracy + variation

    def __call__(self) -> Decimal:
        right_digits = _fake.pyint(min_value=self.min_length, max_value=self.max_length)
        print(self.min_value, self.max_value, right_digits)
        return _fake.pydecimal(
            min_value=self.min_value,  # type: ignore[arg-type]
            max_value=self.max_value,  # type: ignore[arg-type]
            right_digits=right_digits,
        )


class FloatField(AbstractField[float]):
    def __init__(self, min_value: float = 0, max_value: float = 9999) -> None:
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self) -> float:
        return _fake.pyfloat(min_value=self.min_value, max_value=self.max_value)


class CharField(AbstractField[str]):
    def __init__(
        self, *, include_uppercase: bool = False, include_digits: bool = False
    ) -> None:
        alphabet = string.ascii_lowercase
        if include_uppercase:
            alphabet += string.ascii_uppercase
        if include_digits:
            alphabet += string.digits
        self.alphabet = alphabet

    def __call__(self) -> str:
        return choice(self.alphabet)


class StringField(AbstractField[str]):
    def __init__(
        self,
        min_chars: int = 1,
        max_chars: int = 20,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        self.min_chars = min_chars
        self.max_chars = max_chars
        self.prefix = prefix
        self.suffix = suffix

    def __call__(self) -> str:
        return _fake.pystr(
            min_chars=self.min_chars,
            max_chars=self.max_chars,
            prefix=self.prefix,
            suffix=self.suffix,
        )


class DateTimeField(AbstractField[datetime]):
    def __init__(
        self,
        min_datetime: datetime = datetime(2010, 1, 1, tzinfo=UTC),
        max_datetime: datetime = datetime(2030, 12, 31, tzinfo=UTC),
    ) -> None:
        self.timezone = min_datetime.tzinfo
        self.min_datetime = min_datetime.astimezone(UTC)
        self.max_datetime = max_datetime.astimezone(UTC)

    def __call__(self) -> datetime:
        naive_datetime = _fake.date_time_between_dates(
            self.min_datetime, self.max_datetime
        )
        return naive_datetime.replace(tzinfo=self.timezone)


class NaiveDateTimeField(AbstractField[datetime]):
    def __init__(
        self,
        min_datetime: datetime = datetime(2010, 1, 1),  # noqa: DTZ001
        max_datetime: datetime = datetime(2030, 12, 31),  # noqa: DTZ001
    ) -> None:
        self.min_datetime = min_datetime.replace(tzinfo=None)
        self.max_datetime = max_datetime.replace(tzinfo=None)

    def __call__(self) -> datetime:
        return _fake.date_time_between_dates(self.min_datetime, self.max_datetime)


class DateField(AbstractField[date]):
    def __init__(
        self, min_date: date = date(2010, 1, 1), max_date: date = date(2030, 12, 31)
    ) -> None:
        self.min_date = min_date
        self.max_date = max_date

    def __call__(self) -> date:
        return _fake.date_between_dates(self.min_date, self.max_date)


class TimedeltaField(AbstractField[timedelta]):
    def __init__(
        self,
        min_timedelta: timedelta = timedelta(0),
        max_timedelta: timedelta = timedelta(days=365),
    ) -> None:
        self.min_timedelta = min_timedelta
        self.max_timedelta = max_timedelta

    def __call__(self) -> timedelta:
        timedelta = _fake.time_delta(self.max_timedelta - self.min_timedelta)
        return self.min_timedelta + timedelta


class TimezoneField(AbstractField[ZoneInfo]):
    def __init__(self, areas: tuple[str, ...] = ()) -> None:
        areas = areas or (
            "Africa",
            "America",
            "Antarctica",
            "Arctic",
            "Asia",
            "Atlantic",
            "Australia",
            "Europe",
            "Indian",
            "Pacific",
            "Etc",
        )
        self.valid_zones = [
            ZoneInfo(zone)
            for zone in get_timezones()
            if any(zone.startswith(area) for area in areas)
            or (zone == "UTC" and "Etc" in areas)
        ]

    def __call__(self) -> ZoneInfo:
        return choice(self.valid_zones)


class TimeField(AbstractField[time]):
    def __init__(
        self, *, min_time: time = time(0), max_time: time = time(23, 59, 59, 999999)
    ) -> None:
        self._day = date(1970, 1, 1)
        self.min_time = min_time
        self.max_time = max_time
        self._min_datetime = datetime.combine(self._day, self.min_time)
        self._max_datetime = datetime.combine(self._day, self.max_time)

    def __call__(self) -> time:
        timedelta = _fake.time_delta(self._max_datetime - self._min_datetime)
        return (self._min_datetime + timedelta).time()


class TextField(AbstractField[str]):
    def __init__(self, text_type: TextType | UnstableTextType, **kwargs: Any) -> None:
        self.text_type = text_type
        self.kwargs = kwargs

    def __call__(self) -> str:
        relaxed = self.text_type.lower().replace(" ", "_").replace("-", "_")
        faker = getattr(_fake, relaxed)
        return cast(str, faker(**self.kwargs))


class ListField(AbstractField[list[T]]):
    def __init__(
        self, field: AbstractField[T], length: int = 5, variation: int = 0
    ) -> None:
        self.field = field
        self.min_length = length - variation
        self.max_length = length + variation

    def __call__(self) -> list[T]:
        length = _fake.pyint(min_value=self.min_length, max_value=self.max_length)
        return [self.field() for _ in range(length)]


class TupleField(AbstractField[tuple[T, ...]]):
    def __init__(
        self, field: AbstractField[T], length: int = 5, variation: int = 0
    ) -> None:
        self.field = field
        self.min_length = length - variation
        self.max_length = length + variation

    def __call__(self) -> tuple[T, ...]:
        length = _fake.pyint(min_value=self.min_length, max_value=self.max_length)
        return tuple(self.field() for _ in range(length))


class SetField(AbstractField[set[T]]):
    def __init__(
        self, field: AbstractField[T], length: int = 5, variation: int = 0
    ) -> None:
        self.field = field
        self.min_length = length - variation
        self.max_length = length + variation

    def __call__(self) -> set[T]:
        length = _fake.pyint(min_value=self.min_length, max_value=self.max_length)
        return {self.field() for _ in range(length)}


class DictField(AbstractField[dict[K, T]]):
    def __init__(
        self,
        key_field: AbstractField[K],
        value_field: AbstractField[T],
        length: int = 5,
        variation: int = 0,
    ) -> None:
        self.key_field = key_field
        self.value_field = value_field
        self.min_length = length - variation
        self.max_length = length + variation

    def __call__(self) -> dict[K, T]:
        length = _fake.pyint(min_value=self.min_length, max_value=self.max_length)
        return {self.key_field(): self.value_field() for _ in range(length)}


class FactoryField(AbstractField[T]):
    def __init__(self, factory: type[Factory[T]]) -> None:
        self.factory = factory

    def __call__(self) -> Any:
        return self.factory.build()
