import argparse
from . import clargs
import typing as t


class BooleanOptionalActionException(Exception):
    pass


def BooleanOptionalActionWitoutImplicitDefault(option_strings, dest, **kwargs):
    if "default" not in kwargs and "required" not in kwargs:
        kwargs["required"] = True
    if not option_strings:
        raise BooleanOptionalActionException(
            "Flag error, trying to add the flag to a positional parameter?"
        )
    return argparse.BooleanOptionalAction(option_strings, dest, **kwargs)


Flag = t.Annotated[
    bool,
    clargs.extra_info(
        type=clargs.UNSET,
        nargs=clargs.UNSET,
        action=BooleanOptionalActionWitoutImplicitDefault,
    ),
]

Count = t.Annotated[
    int,
    clargs.extra_info(
        type=clargs.UNSET,
        nargs=clargs.UNSET,
        action="count",
        default=0,
        required=False,
    ),
]

TYPE = t.TypeVar("TYPE")
ListOfAtLeastOne = t.Annotated[list[TYPE], clargs.extra_info(nargs="+")]
