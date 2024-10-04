from __future__ import annotations

import string
from decimal import Decimal
from secrets import choice
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from faker import Faker

if TYPE_CHECKING:
    from collections.abc import Iterable

    from factorio.factories import Factory
    from factorio.types import TextType

_fake = Faker()

K = TypeVar("K")
T = TypeVar("T")


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


class TextField(AbstractField[str]):
    def __init__(self, text_type: TextType, **kwargs: Any) -> None:
        self.text_type = text_type
        self.kwargs = kwargs

    def __call__(self) -> str:
        faker = getattr(_fake, self.text_type)
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
