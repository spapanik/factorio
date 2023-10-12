from __future__ import annotations

from typing import Any

from factorio.fields import AbstractField


class Factory:
    Fields: type

    class Meta:
        model: type

    @classmethod
    def build(cls, **kwargs: Any) -> Any:
        fields: dict[str, Any] = kwargs
        for key, value in cls.Fields.__dict__.items():
            if key.startswith("__") and key.endswith("__"):
                continue

            if key in kwargs:
                value = kwargs[key]  # noqa: PLW2901

            fields[key] = value() if isinstance(value, AbstractField) else value

        return cls.Meta.model(**fields)
