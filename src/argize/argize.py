import argparse
import inspect
import pathlib
import functools
import types
import typing as t
import dataclasses

# simple types are those types that have a constructor taking a single str
SIMPLE_TYPES = (str, int, float, pathlib.Path)


class NOT_SET_TYPE:
    singleton = None

    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def __bool__(self):
        return False


NOT_SET = NOT_SET_TYPE()

T = t.TypeVar("T", bound=t.Type)


@dataclasses.dataclass(kw_only=True)
class Params(t.Generic[T]):

    action: NOT_SET_TYPE | t.Literal[
        'store', 'store_const', 'store_true', 'append',
        'append_const', 'count', 'help', 'version'] = NOT_SET
    const: NOT_SET_TYPE | T = NOT_SET
    choices: NOT_SET_TYPE | t.Container[T] = NOT_SET
    default: NOT_SET_TYPE | T = NOT_SET
    dest: NOT_SET_TYPE | str = NOT_SET
    help: NOT_SET_TYPE | str = NOT_SET
    nargs: NOT_SET_TYPE | int | t.Literal["?", "*", "+"] = NOT_SET
    required: NOT_SET_TYPE | bool = NOT_SET
    metavar: NOT_SET_TYPE | str = NOT_SET
    type: NOT_SET_TYPE | t.Callable[[str], T] = NOT_SET
    aliases: NOT_SET_TYPE | t.Sequence["str"] = NOT_SET

    def combine_with(self, other: "Params[T]"):
        return type(self)(**{
            **{k: v for k, v in self.asdict().items() if v is not NOT_SET},
            **{k: v for k, v in other.asdict().items() if v is not NOT_SET},
        })

    def asdict(self):
        return dataclasses.asdict(self)

    def add_to_parser(
            self,
            name: str,
            positional: bool,
            parser: argparse.ArgumentParser,
            default: NOT_SET_TYPE | T,
            typ: t.Type[T],
    ):
        name_as_param = name.replace("_", "-")
        positional_args = (("" if positional else "--") + name_as_param,
                           *(self.aliases or []))
        kwargs = {k: v for k, v in self.asdict().items()
                  if k != "aliases" and v is not NOT_SET}
        if "type" not in kwargs:
            if typ == bool:
                positional_args, newkwargs = get_args_for_bool(
                        name_as_param, positional, positional_args, default)
                kwargs = {**newkwargs, **kwargs}
            else:
                kwargs = {**get_args_from_type_and_default(typ, default),
                          **kwargs}
        if "default" not in kwargs and default is not NOT_SET:
            kwargs["default"] = default
            kwargs["nargs"] = "?"

        parser.add_argument(*positional_args, **kwargs)


class GetArgsFromTypeException(Exception):
    pass


def get_args_for_bool(
    name_as_param: str,
    positional: bool,
    positional_args: list[str],
    default: bool | NOT_SET_TYPE,
) -> (list[str], dict):
    if positional:
        raise GetArgsFromTypeException(
            f"{name_as_param}: Boolean types can only be used "
            "in keyword-only arguments")
    if default is False:
        return (positional_args, {
            "action": "store_const", "const": True, "default": False})
    if default is True:
        if not all(arg.startswith("--") for arg in positional_args):
            raise GetArgsFromTypeException(
                f"{name_as_param}: Boolean types with True as "
                "default value cannot have aliases that start "
                "with something else than `--`")

        new_positional_args = [
                f"--no-{arg[len('--'):]}" for arg in positional_args]
        return (new_positional_args, {
            "action": "store_const", "const": False, "default": True,
            "dest": name_as_param})
    raise GetArgsFromTypeException(
        f"{name_as_param}: Boolean types always need a default value"
        "in keyword-only arguments")


def handle_literal(typ: t.Type[T]):
    args = t.get_args(typ)
    if len(args) == 0:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "Literal with no items is not supported")
    for basetyp in SIMPLE_TYPES:
        if all(isinstance(arg, basetyp) for arg in args):
            return {"type": basetyp, "choices": args}
    else:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "All items should be of the same empty type.")


def handle_union(typ: t.Type[T], default: T | NOT_SET):
    args = list(t.get_args(typ))
    if len(args) != 2 or type(None) not in args:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "Unions not supported (unless Union with None.")
    try:
        args.remove(type(None))
        return get_args_from_type_and_default(
            args[0], default, simple=True)
    except GetArgsFromTypeException:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "Type within Optional must be simple type")


def handle_list(typ: t.Type[T], default: T | NOT_SET):
    args = t.get_args(typ)
    assert len(args) == 1
    try:
        itemargs = get_args_from_type_and_default(
            args[0], default, simple=True)
    except GetArgsFromTypeException:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "Type within List must be simple type.")
    assert set(itemargs.keys()) - {"type", "choice"}  # TODO better error
    return {
        **itemargs,
        "nargs": "*",
    }


def issubclass_rugged(subcls, parentcls) -> bool:
    try:
        return issubclass(subcls, parentcls)
    except TypeError:
        return False


def get_args_from_type_and_default(
    typ: t.Type[T], default: T | NOT_SET, *,
    simple: bool = False,
) -> dict:
    if issubclass_rugged(typ, bool):
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "Bool is not allowed in this context.")
    origin = t.get_origin(typ)
    if origin == t.Literal:
        return handle_literal(typ)
    if issubclass_rugged(typ, SIMPLE_TYPES):
        return {"type": typ}
    if simple:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "Expected simple type.")

    if origin == t.Union or origin == types.UnionType:  # noqa
        return handle_union(typ, default)
    if issubclass_rugged(origin, t.Sequence):
        return handle_list(typ, default)
    if origin:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "Complex types beyond Literal, Optional and List not supported.")
    else:
        raise GetArgsFromTypeException(
            f"Problem generating parsing function for {typ}; "
            "No code how how to deal with this type")


def create_parser(func: t.Callable) -> argparse.ArgumentParser:
    docstring = inspect.getdoc(func) or ""
    first_paragraph = \
        [*[p for p in docstring.split("\n\n") if p.strip()], ""][0]

    parser = argparse.ArgumentParser(
        description=first_paragraph,
    )
    add_to_parser(parser, func)
    return parser


def add_to_parser(parser: argparse.ArgumentParser, func: t.Callable) -> None:
    parser.set_defaults(_argize_func_=func)
    signature = inspect.signature(func)
    for param in signature.parameters.values():
        typehint = str if param.annotation is inspect.Parameter.empty \
            else param.annotation
        default = NOT_SET if param.default is inspect.Parameter.empty \
            else param.default
        if param.kind not in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY):
            raise GetArgsFromTypeException(
                "variable-length-arguments (those starting with * and **) "
                "are not (yet) supported")
        positional = param.kind != inspect.Parameter.KEYWORD_ONLY
        (typ, *metas) = t.get_args(typehint) \
            if t.get_origin(typehint) == t.Annotated else (typehint, )
        params = functools.reduce(
            lambda a, b: a.combine_with(b) if isinstance(b, Params) else a,
            reversed(metas), Params(), )
        params.add_to_parser(param.name, positional, parser, default, typ)


def run(args):
    assert "_argize_func_" in args
    return args._argize_func_(
            **{k: v for k, v in vars(args).items() if k != "_argize_func_"})
