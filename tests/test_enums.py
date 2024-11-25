from factorio.lib.enums import StrEnum


def test_str() -> None:
    class MyEnum(StrEnum):
        FOO = "foo"
        BAR = "bar"

    assert str(MyEnum.FOO) == "foo"
    assert str(MyEnum.BAR) == "bar"


def test_eq() -> None:
    class MyEnum(StrEnum):
        FOO = "foo"
        BAR = "bar"

    class Equal:
        def __eq__(self, other: object) -> bool:
            return True

    assert MyEnum.FOO == "foo"
    assert MyEnum.FOO == MyEnum.FOO
    assert MyEnum.FOO == Equal()  # noqa: SIM300
    assert MyEnum.FOO != "bar"
    assert MyEnum.FOO != MyEnum.BAR
    assert MyEnum.BAR != 3.14
