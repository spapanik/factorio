from factorio.enums import StrEnum


def test_str() -> None:
    class MyEnum(StrEnum):
        FOO = "foo"
        BAR = "bar"

    assert str(MyEnum.FOO) == "foo"
    assert str(MyEnum.BAR) == "bar"
