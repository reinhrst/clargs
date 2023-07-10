import argparse
from . import argize
import typing as t


class BooleanOptionalActionException(Exception):
    pass


def BooleanOptionalActionWitoutImplicitDefault(option_strings, dest, **kwargs):
    if "default" not in kwargs and "required" not in kwargs:
        kwargs["required"] = True
    if not option_strings:
        raise BooleanOptionalActionException(
            "Flag error, trying to add the flag to a positional parameter?")
    return argparse.BooleanOptionalAction(option_strings, dest, **kwargs)


Flag = t.Annotated[
        bool,
        argize.extra_info(
            type=argize.UNSET,
            nargs=argize.UNSET,
            action=BooleanOptionalActionWitoutImplicitDefault,
        )]

Count = t.Annotated[
        int,
        argize.extra_info(
            type=argize.UNSET,
            nargs=argize.UNSET,
            action="count",
            default=0,
        )]
