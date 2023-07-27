from __future__ import annotations
import argparse
import inspect
import pathlib
import logging
import dataclasses
import typing as t
from . import aap_from_data
from . import docsparser

logger = logging.getLogger("clargs")

# simple types are those types that have a constructor taking a single str
SIMPLE_TYPES = (str, int, float, pathlib.Path)


class NOT_SET_TYPE:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"NOT_SET_TYPE({id})"

    def __copy__(self):
        return self

    def __deepcopy__(self, *args):
        return self

    def __bool__(self):
        return False


NOT_SET = NOT_SET_TYPE("not_set")
UNSET = NOT_SET_TYPE("unset")

T = t.TypeVar("T")
RET = t.TypeVar("RET")


class ExtraInfoException(Exception):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Settings:
    flag_prefix: str = "--"
    short_flag_prefix: t.Optional[str] = "-"
    generate_short_flags: bool = True
    positional_and_kw_args_become: t.Literal[
        "positional", "flag_if_default", "flag"
    ] = "positional"
    replace_underscore_with_dash: bool = True

    def __post_init__(self):
        assert not (self.short_flag_prefix is None and self.generate_short_flags), (
            "If generate_short_flags is True, short_flag_prefix " "cannot be None"
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AddArgumentParameters(t.Generic[T]):
    action: t.Literal[
        "store",
        "store_const",
        "store_true",
        "store_false",
        "append",
        "append_const",
        "count",
        "help",
        "version",
    ] | t.Callable | NOT_SET_TYPE = NOT_SET
    choices: t.Container[str] | NOT_SET_TYPE = NOT_SET
    const: T | NOT_SET_TYPE = NOT_SET
    default: T | NOT_SET_TYPE = NOT_SET
    dest: str | NOT_SET_TYPE = NOT_SET
    help: str | NOT_SET_TYPE = NOT_SET
    metavar: str | NOT_SET_TYPE = NOT_SET
    nargs: int | t.Literal["?", "*", "+"] | NOT_SET_TYPE = NOT_SET
    required: bool | NOT_SET_TYPE = NOT_SET
    type: t.Callable[[str], T] | NOT_SET_TYPE = NOT_SET

    def with_fields(
        self, fields: dict | AddArgumentParameters[T]
    ) -> AddArgumentParameters[T]:
        fieldsdict = (
            fields.asdict(keep_unset=True)
            if isinstance(fields, AddArgumentParameters)
            else fields
        )
        return AddArgumentParameters(
            **{
                **self.asdict(keep_unset=True),
                **fieldsdict,
            }
        )

    def asdict(self, keep_unset=False):
        return {
            k: v
            for k, v in dataclasses.asdict(self).items()
            if v is not NOT_SET and (keep_unset or v is not UNSET)
        }


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExtraInfo(t.Generic[T]):
    add_argument_parameters: AddArgumentParameters[T] = dataclasses.field(
        default_factory=AddArgumentParameters
    )
    name: str | NOT_SET_TYPE = NOT_SET
    aliases: t.Sequence["str"] | NOT_SET_TYPE = NOT_SET
    validate: t.Callable[[T], bool] | NOT_SET_TYPE = NOT_SET
    mapping: t.Mapping[str, T] | NOT_SET_TYPE = NOT_SET

    def __post_init__(self):
        if self.mapping is not NOT_SET and self.add_argument_parameters.type:
            raise ExtraInfoException("You cannot set both mapping and type keys")
        if isinstance(self.aliases, str):
            raise ExtraInfoException(
                "aliases must be list, not string (did you forget `[]`?)"
            )


def extra_info(
    *,
    name: str | NOT_SET_TYPE = NOT_SET,
    aliases: t.Sequence["str"] | NOT_SET_TYPE = NOT_SET,
    validate: t.Callable[[T], bool] | NOT_SET_TYPE = NOT_SET,
    mapping: t.Mapping[str, T] | NOT_SET_TYPE = NOT_SET,
    action: t.Literal[
        "store",
        "store_const",
        "store_true",
        "store_false",
        "append",
        "append_const",
        "count",
        "help",
        "version",
    ]
    | t.Callable
    | NOT_SET_TYPE = NOT_SET,
    choices: t.Container[str] | NOT_SET_TYPE = NOT_SET,
    const: T | NOT_SET_TYPE = NOT_SET,
    default: T | NOT_SET_TYPE = NOT_SET,
    dest: str | NOT_SET_TYPE = NOT_SET,
    help: str | NOT_SET_TYPE = NOT_SET,
    metavar: str | NOT_SET_TYPE = NOT_SET,
    nargs: int | t.Literal["?", "*", "+"] | NOT_SET_TYPE = NOT_SET,
    required: bool | NOT_SET_TYPE = NOT_SET,
    type: t.Callable[[str], T] | NOT_SET_TYPE = NOT_SET,
) -> ExtraInfo:
    return ExtraInfo(
        name=name,
        aliases=aliases,
        validate=validate,
        mapping=mapping,
        add_argument_parameters=AddArgumentParameters(
            action=action,
            choices=choices,
            const=const,
            default=default,
            dest=dest,
            help=help,
            metavar=metavar,
            nargs=nargs,
            required=required,
            type=type,
        ),
    )


class Clargs:
    settings: Settings

    def __init__(self, settings: t.Optional[Settings] = None):
        self.settings = settings or Settings()

    def create_parser(self, func: t.Callable[..., RET]) -> argparse.ArgumentParser:
        docstring = inspect.getdoc(func) or ""
        first_paragraph = [*[p for p in docstring.split("\n\n") if p.strip()], ""][0]

        prefix_chars = "".join(
            set(
                self.settings.flag_prefix
                + (
                    (self.settings.short_flag_prefix or "")
                    if self.settings.generate_short_flags
                    else ""
                )
            )
        )
        parser = argparse.ArgumentParser(
            description=first_paragraph,
            prefix_chars=prefix_chars,
        )
        self.add_to_parser(parser, func)
        return parser

    def add_to_parser(self, parser: argparse.ArgumentParser, func: t.Callable) -> None:
        parser.set_defaults(_clargs_func_=func)
        signature = inspect.signature(func)
        docstring = inspect.getdoc(func) or ""
        paramdescriptions = {
            p.name: p.description
            for p in docsparser.get_parameter_info_from_docstring(docstring)
        }
        args_and_aap_s: t.Sequence[t.Tuple[t.Sequence[str], AddArgumentParameters]] = [
            aap_from_data.AapFromData.from_param_and_settings(
                param, paramdescriptions.get(param.name, None), self.settings
            ).get_args_and_aap()
            for param in signature.parameters.values()
        ]

        args_and_aap_s = Clargs._filter_out_taken_names_from_auto_names(args_and_aap_s)

        for (args, aap), param in zip(args_and_aap_s, signature.parameters.values()):
            logger.debug("Adding %s", repr((args, aap.asdict())))
            from . import helper_types

            try:
                parser.add_argument(*args, **aap.asdict())
            except helper_types.BooleanOptionalActionException:
                raise aap_from_data.GetArgsFromTypeException(
                    param,
                    "Flag error, are you trying to use Flag in a "
                    "positional argument?",
                )

    def add_subparser(self, subparsers, func: t.Callable):
        docstring = inspect.getdoc(func) or ""
        first_paragraph = [*[p for p in docstring.split("\n\n") if p.strip()], ""][0]
        func_name_with_replacement = (
            func.__name__.replace("_", "-")
            if self.settings.replace_underscore_with_dash
            else func.__name__
        )
        subparser = subparsers.add_parser(
            func_name_with_replacement, help=first_paragraph
        )
        self.add_to_parser(subparser, func)

    @staticmethod
    def _filter_out_taken_names_from_auto_names(args_and_aap_s):
        taken_names = set(
            name
            for names, _ in args_and_aap_s
            for name in names
            if not isinstance(name, aap_from_data.AutoGeneratedShortName)
        )

        new_args_and_aap_s = []
        for names, aap in args_and_aap_s:
            new_names = []
            for name in names:
                if not isinstance(name, aap_from_data.AutoGeneratedShortName):
                    new_names.append(name)
                    continue
                assert isinstance(name, aap_from_data.AutoGeneratedShortName)
                str_name = str(name)
                del name
                if str_name in taken_names:
                    pass
                else:
                    new_names.append(str_name)
                    taken_names.add(str_name)
            assert new_names
            new_args_and_aap_s.append((new_names, aap))
        return new_args_and_aap_s

    @staticmethod
    def run(args):
        logger.debug("Received parsed args %s", args)
        assert "_clargs_func_" in args
        function = args._clargs_func_
        positional_parameters = [
            param
            for param in inspect.signature(function).parameters.values()
            if param.kind == inspect.Parameter.POSITIONAL_ONLY
        ]
        argsdict = vars(args)
        args = {p.name: argsdict[p.name] for p in positional_parameters}
        kwargs = {
            k: v for k, v in argsdict.items() if k != "_clargs_func_" and k not in args
        }
        return function(*args.values(), **kwargs)

    def create_parser_and_run(self, func: t.Callable[..., RET], args=None) -> RET:
        parser = self.create_parser(func)
        return Clargs.run(parser.parse_args(args))


def create_parser(func: t.Callable) -> argparse.ArgumentParser:
    return Clargs().create_parser(func)


def add_to_parser(parser: argparse.ArgumentParser, func: t.Callable) -> None:
    return Clargs().add_to_parser(parser, func)


def add_subparser(subparsers, func: t.Callable) -> None:
    return Clargs().add_subparser(subparsers, func)


def run(args):
    return Clargs.run(args)


def create_parser_and_run(func: t.Callable[..., RET], args=None) -> RET:
    return Clargs().create_parser_and_run(func, args)
