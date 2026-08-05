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

    class SpamAndBaconFactory(SpamFactory, BaconFactory):  # ty: ignore[invalid-generic-class]
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


def test_build_with_documented_admin_user_factory() -> None:
    @dataclass
    class User:
        name: str
        email: str
        role: str
        is_admin: bool

    class BaseUserFactory(Factory[User]):
        name = fields.TextField("name")
        email = fields.TextField("email")

    class AdminUserFactory(BaseUserFactory):
        role = fields.ConstantField("admin")
        is_admin = fields.ConstantField(True)  # noqa: FBT003

    admin = AdminUserFactory.build()

    assert isinstance(admin.name, str)
    assert isinstance(admin.email, str)
    assert admin.role == "admin"
    assert admin.is_admin is True


def test_build_with_multilevel_inheritance_and_field_override() -> None:
    @dataclass
    class Record:
        root: str
        middle: str
        leaf: str

    class RootFactory(Factory[Record]):
        root = fields.ConstantField("root")
        middle = fields.ConstantField("root override")

    class MiddleFactory(RootFactory):
        middle = fields.ConstantField("middle")

    class LeafFactory(MiddleFactory):
        leaf = fields.ConstantField("leaf")

    assert LeafFactory.build() == Record(root="root", middle="middle", leaf="leaf")


def test_build_with_multiple_inheritance() -> None:
    @dataclass
    class Article:
        created_at: str
        created_by: str
        title: str

    class TimestampedFactory(Factory[Article]):
        created_at = fields.ConstantField("yesterday")

    class AuditableFactory(Factory[Article]):
        created_by = fields.ConstantField("alice")

    class ArticleFactory(TimestampedFactory, AuditableFactory):
        title = fields.ConstantField("Factorio")

    assert ArticleFactory.build() == Article(
        created_at="yesterday", created_by="alice", title="Factorio"
    )


def test_build_with_diamond_inheritance_uses_mro_precedence() -> None:
    @dataclass
    class Record:
        root: str
        left: str
        right: str
        leaf: str
        shared: str

    class RootFactory(Factory[Record]):
        root = fields.ConstantField("root")
        shared = fields.ConstantField("root")

    class LeftFactory(RootFactory):
        left = fields.ConstantField("left")
        shared = fields.ConstantField("left")

    class RightFactory(RootFactory):
        right = fields.ConstantField("right")
        shared = fields.ConstantField("right")

    class LeafFactory(LeftFactory, RightFactory):
        leaf = fields.ConstantField("leaf")

    assert LeafFactory.build() == Record(
        root="root", left="left", right="right", leaf="leaf", shared="left"
    )
