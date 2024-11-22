from __future__ import annotations

from inspect import getmro
from typing import Any, Generic, TypeVar
from warnings import warn

from factorio.fields import AbstractField
from factorio.lib.exceptions import RemovedIn07Warning

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
    def build(cls, **kwargs: Any) -> T:
        if hasattr(cls, "Fields"):
            return cls._old_style_build(**kwargs)

        model = cls.get_model()
        fields: dict[str, Any] = {}
        for key, value in cls.__dict__.items():
            if isinstance(value, AbstractField):
                fields[key] = value()
        for key, value in kwargs.items():
            fields[key] = value() if isinstance(value, AbstractField) else value

        return model(**fields)

    @classmethod
    def _old_style_build(cls, **kwargs: Any) -> T:
        warning = RemovedIn07Warning(
            "Factories with `Fields` class", "ConstantField for constant values"
        )
        warn(warning, stacklevel=3)
        model = cls.get_model()
        fields: dict[str, Any] = kwargs
        for key, value in cls.Fields.__dict__.items():
            if key.startswith("__") and key.endswith("__"):
                continue

            if key in kwargs:
                value = kwargs[key]  # noqa: PLW2901

            fields[key] = value() if isinstance(value, AbstractField) else value

        return model(**fields)
