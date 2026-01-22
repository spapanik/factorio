import pytest


@pytest.mark.filterwarnings("ignore:TextType")
def test_str() -> None:
    from factorio.lib.enums import StrEnum  # noqa: PLC0415

    class MyEnum(StrEnum):
        FOO = "foo"
        BAR = "bar"

    assert str(MyEnum.FOO) == "foo"
    assert str(MyEnum.BAR) == "bar"


@pytest.mark.filterwarnings("ignore:TextType")
def test_hash() -> None:
    from factorio.lib.enums import StrEnum  # noqa: PLC0415

    class MyEnum(StrEnum):
        FOO = "foo"

    assert hash(MyEnum.FOO) == hash("foo")


@pytest.mark.filterwarnings("ignore:TextType")
def test_eq() -> None:
    from factorio.lib.enums import StrEnum  # noqa: PLC0415

    class MyEnum(StrEnum):
        FOO = "foo"
        BAR = "bar"

    class Equal:  # noqa: PLW1641
        def __eq__(self, other: object) -> bool:
            return True

    assert MyEnum.FOO == "foo"
    assert MyEnum.FOO == MyEnum.FOO
    assert MyEnum.FOO == Equal()  # noqa: SIM300
    assert MyEnum.FOO != "bar"
    assert MyEnum.FOO != MyEnum.BAR
    assert MyEnum.BAR != 3.14
