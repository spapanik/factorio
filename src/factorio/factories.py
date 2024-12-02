from __future__ import annotations

from inspect import getmro
from typing import Generic, TypeVar

from factorio.fields import AbstractField

T = TypeVar("T")


class Factory(Generic[T]):
    Fields: type

    @classmethod
    def get_model(cls) -> type[T]:
        candidates: set[type] = set()
        for base in getmro(cls):
            for original_base in getattr(base, "__orig_bases__", ()):
                args = getattr(original_base, "__args__", ())
                candidates.update(arg for arg in args if not isinstance(arg, TypeVar))

        if len(candidates) > 1:
            msg = f"Multiple concrete models found for {cls.__name__}"
            raise TypeError(msg)

        if not candidates:
            msg = f"No concrete model found for {cls.__name__}"
            raise TypeError(msg)

        return candidates.pop()

    @classmethod
    def build(cls, **kwargs: object) -> T:
        model = cls.get_model()
        fields = {
            key: value()
            for key, value in cls.__dict__.items()
            if isinstance(value, AbstractField)
        }
        for key, value in kwargs.items():
            fields[key] = value() if isinstance(value, AbstractField) else value

        return model(**fields)
