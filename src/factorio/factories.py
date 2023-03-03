from __future__ import annotations

from typing import Any

from factorio.fields import AbstractField


class Factory:
    class Meta:
        model: type
        fields: dict[str, Any]

    @classmethod
    def build(cls, **kwargs):
        fields: dict[str, Any] = {}
        for key, value in cls.Meta.fields.items():
            if key in kwargs:
                value = kwargs[key]  # noqa: PLW2901

            fields[key] = value() if isinstance(value, AbstractField) else value

        return cls.Meta.model(**fields)
