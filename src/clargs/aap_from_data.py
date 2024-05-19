from __future__ import annotations
import inspect
from . import clargs
import types
import typing as t
import pathlib
import dataclasses

T = t.TypeVar("T")


def parse_bool(val: str) -> bool:
    if val.lower() in {"yes", "true"}:
        return True
    if val.lower() in {"no", "false"}:
        return False
    raise ValueError(f"Don't know to to parse {val} into bool")


SIMPLE_TYPES: t.Mapping[t.Any, t.Callable[[str], t.Any]] = {
    str: str,
    int: int,
    float: float,
    pathlib.Path: pathlib.Path,
    bool: parse_bool,
}


class AutoGeneratedShortName(str):
    pass


class GetArgsFromTypeException(Exception):
    def __init__(self, param: inspect.Parameter, msg: str):
        return super().__init__(
            f"{param.name}: Cannot parse type {param.annotation}.\n{msg}"
        )


def issubclass_rugged(subcls, parentcls) -> bool:
    try:
        return issubclass(subcls, parentcls)
    except TypeError:
        return False


@dataclasses.dataclass(frozen=True, kw_only=True)
class AapFromData(t.Generic[T]):
    typ: t.Type[T]
    param: inspect.Parameter
    settings: clargs.Settings
    extra_info: clargs.ExtraInfo
    docstring_description: t.Optional[str]

    @classmethod
    def from_param_and_settings(
        cls,
        param: inspect.Parameter,
        docstring_description: t.Optional[str],
        settings: clargs.Settings,
    ) -> AapFromData[T]:
        if param.kind not in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            raise GetArgsFromTypeException(
                param,
                "variable-length-arguments (those starting with * and **) "
                "are not (yet) supported",
            )

        typehint = (
            str if param.annotation is inspect.Parameter.empty else param.annotation
        )
        (typ, *metadatas) = (
            t.get_args(typehint)
            if t.get_origin(typehint) == t.Annotated
            else (typehint, [])
        )

        if t.get_origin(typ) == t.Union or t.get_origin(typ) == types.UnionType:  # noqa
            # check for Optional[]; if so, remove
            args = list(t.get_args(typ))
            if len(args) == 2 and type(None) in args:
                typehint = args[0] if args[1] is type(None) else args[1]  # noqa
                (typ, *extra_metadatas) = (
                    t.get_args(typehint)
                    if t.get_origin(typehint) == t.Annotated
                    else (typehint, [])
                )
                metadatas = [*metadatas, *extra_metadatas]

        extra_infos = [
            *(md for md in metadatas if isinstance(md, clargs.ExtraInfo)),
        ]
        if len(extra_infos) > 1:
            raise GetArgsFromTypeException(param, "Can only have one ExtraInfo")
        extra_info = extra_infos[0] if extra_infos else clargs.ExtraInfo()

        return cls(
            typ=typ,
            param=param,
            docstring_description=docstring_description,
            settings=settings,
            extra_info=extra_info,
        )

    def has_default(self) -> bool:
        return self.param.default is not inspect.Parameter.empty

    def get_all_param_names(self) -> t.Sequence[str]:
        has_custom_name = self.extra_info.name is not clargs.NOT_SET
        param_name_with_replacement = (
            self.param.name.replace("_", "-")
            if self.settings.replace_underscore_with_dash and self.arg_type_is_flag()
            else self.param.name
        )
        param_name = t.cast(
            str,
            self.extra_info.name
            if has_custom_name
            else ("" if self.arg_type_is_positional() else self.settings.flag_prefix)
            + param_name_with_replacement,
        )
        all_param_names = [
            param_name,
            *(t.cast(list[str], self.extra_info.aliases or [])),
        ]
        if self.arg_type_is_flag() and self.settings.generate_short_flags:
            if param_name.startswith(self.settings.flag_prefix):
                assert isinstance(self.settings.short_flag_prefix, str)
                shortname = param_name[len(self.settings.flag_prefix)]
                all_param_names.append(
                    AutoGeneratedShortName(self.settings.short_flag_prefix + shortname)
                )
        return tuple(all_param_names)

    def arg_type_is_positional(self) -> bool:
        if self.param.kind == inspect.Parameter.POSITIONAL_ONLY:
            return True
        if self.param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if self.settings.positional_and_kw_args_become == "positional":
                return True
            if self.settings.positional_and_kw_args_become == "flag":
                return False
            if self.param.default is inspect.Parameter.empty:
                return True
        return False

    def arg_type_is_flag(self) -> bool:
        return not self.arg_type_is_positional()

    def handle_simple_type(
        self, *, override_typ=None
    ) -> None | clargs.AddArgumentParameters[T]:
        typ = override_typ or self.typ
        handler = SIMPLE_TYPES.get(typ)
        if handler:
            return clargs.AddArgumentParameters(type=handler)
        return None

    def handle_explicit_type(self) -> None | clargs.AddArgumentParameters[T]:
        if isinstance(
            self.extra_info.add_argument_parameters.type, clargs.NOT_SET_TYPE
        ):
            return None
        return self.extra_info.add_argument_parameters

    def handle_mapping(self) -> None | clargs.AddArgumentParameters[T]:
        if isinstance(self.extra_info.mapping, clargs.NOT_SET_TYPE):
            return None
        mapping = self.extra_info.mapping
        return clargs.AddArgumentParameters(
            choices=list(mapping.keys()),
            type=lambda x: mapping[x],
        )

    def handle_literal(
        self, *, override_typ=None
    ) -> None | clargs.AddArgumentParameters[T]:
        typ = override_typ or self.typ
        if t.get_origin(typ) != t.Literal:
            return None
        args = t.get_args(typ)
        argtypes = list(set(type(arg) for arg in args))
        if len(argtypes) == 0:
            raise GetArgsFromTypeException(
                self.param, "Literal with no items is not supported"
            )
        if len(argtypes) != 1:
            raise GetArgsFromTypeException(
                self.param, "All literal items should be of the same type."
            )
        result = self.handle_simple_type(override_typ=argtypes[0])
        if not result:
            raise GetArgsFromTypeException(
                self.param, "Cannot parse base type for literal"
            )
        return result.with_fields({"choices": args})

    def handle_list(self) -> None | clargs.AddArgumentParameters[T]:
        if not issubclass_rugged(t.get_origin(self.typ), t.Sequence):
            return None
        if issubclass_rugged(t.get_origin(self.typ), t.Tuple):
            # Tuples not supported
            return None
        args = t.get_args(self.typ)
        assert len(args) == 1
        result = self.handle_simple_type(override_typ=args[0]) or self.handle_literal(
            override_typ=args[0]
        )
        if not result:
            raise GetArgsFromTypeException(
                self.param, "List only supports simple and literal inner types."
            )
        return result.with_fields(
            {
                "nargs": "*",
                "action": "extend",
            }
        )

    def get_args_and_aap(
        self,
    ) -> t.Tuple[t.Sequence[str], clargs.AddArgumentParameters[T]]:
        aap = (
            None
            or self.handle_explicit_type()
            or self.handle_literal()
            or self.handle_simple_type()
            or self.handle_list()
        )
        if not aap:
            raise GetArgsFromTypeException(
                self.param, "Cannot find a rule for this type."
            )
        if self.docstring_description is not None:
            aap = aap.with_fields({"help": self.docstring_description})
        if self.has_default():
            aap = aap.with_fields(
                {
                    "default": self.param.default,
                }
            )

            if self.arg_type_is_flag() and not aap.action:
                aap = aap.with_fields({"required": False})
            else:
                if aap.nargs == clargs.NOT_SET:
                    aap = aap.with_fields({"nargs": "?"})
        else:
            if (
                self.arg_type_is_flag()
                and not aap.action
                and aap.nargs not in ["*", "?"]
            ):
                aap = aap.with_fields({"required": True})

        # overwrite any explicitly set data
        aap = aap.with_fields(self.extra_info.add_argument_parameters)

        if self.extra_info.validate is not clargs.NOT_SET:
            assert not isinstance(aap.type, clargs.NOT_SET_TYPE)
            originaltype = aap.type

            def validate(*args, **kwargs):
                result = originaltype(*args, **kwargs)
                if not self.extra_info.validate(result):
                    raise ValueError("Problem with validation")
                return result

            validate.__name__ = f"{originaltype.__name__}-validation"

            aap = aap.with_fields({"type": validate})

        return (self.get_all_param_names(), aap)
