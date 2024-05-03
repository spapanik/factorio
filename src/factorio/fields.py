from __future__ import annotations

from secrets import choice
from typing import TYPE_CHECKING, Any, Iterable, NoReturn

from faker import Faker

if TYPE_CHECKING:
    from factorio.factories import Factory

_fake = Faker()

ALIASES = {"int": "pyint"}


class AbstractField:
    def __call__(self) -> NoReturn:
        msg = "All concrete fields must be callable"
        raise NotImplementedError(msg)


class Field(AbstractField):
    def __init__(self, type_: str, **kwargs: Any):
        self.type = type_
        self.kwargs = kwargs

    def __call__(self) -> Any:
        return getattr(_fake, ALIASES.get(self.type, self.type))(**self.kwargs)


class ChoiceField(AbstractField):
    def __init__(self, options: Iterable[Any]):
        self.options = list(options)

    def __call__(self) -> Any:
        return choice(self.options)


class CollectionField(AbstractField):
    def __init__(
        self,
        field: AbstractField,
        container: type,
        min_length: int = 1,
        max_length: int = 10,
        length: int | None = None,
    ):
        self.field = field
        self.container = container
        if length is not None:
            min_length = length
            max_length = length
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self) -> Any:
        length = _fake.pyint(min_value=self.min_length, max_value=self.max_length)
        return self.container(self.field() for _ in range(length))


class FactoryField(AbstractField):
    def __init__(self, factory: type[Factory]):
        self.factory = factory

    def __call__(self) -> Any:
        return self.factory.build()
