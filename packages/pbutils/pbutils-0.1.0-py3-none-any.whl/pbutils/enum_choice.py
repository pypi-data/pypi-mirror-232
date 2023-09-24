# https://github.com/pallets/click/pull/2210 がマージされるまでのパッチ

import enum
from typing import Any, Type

import click


class EnumChoice(click.Choice):
    def __init__(self, enum_type: Type[enum.Enum], case_sensitive: bool = True) -> None:
        super().__init__(
            choices=[element.name for element in enum_type],
            case_sensitive=case_sensitive,
        )
        self.enum_type = enum_type

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> Any:
        value = super().convert(value=value, param=param, ctx=ctx)
        if value is None:
            return None
        return self.enum_type[value]
