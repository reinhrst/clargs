import clargs
import unittest
import io
import pathlib
import typing as t
import logging
import sys
import contextlib


def str_func(foo: str):
    assert foo == "foo"
    return "SUCCESS"


def no_annotation_func(foo):
    assert foo == "foo"
    return "SUCCESS"


def int_func(one: int):
    assert one == 1
    return "SUCCESS"


def float_func(pi: float):
    assert pi == 3.14
    return "SUCCESS"


def path_func(etc: pathlib.Path):
    assert etc == pathlib.Path("/etc")
    return "SUCCESS"


def setUpModule():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


def expectedFailureIf(condition):
    """The test is marked as an expectedFailure if the condition is satisfied."""

    def wrapper(func):
        if condition:
            return unittest.expectedFailure(func)
        else:
            return func

    return wrapper


class Base(unittest.TestCase):
    @contextlib.contextmanager
    def assertExit(self, *, msg: t.Optional[str] = None, regex: t.Optional[str] = None):
        capture = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(capture):
            yield
        capturestr = capture.getvalue()
        del capture
        print(capturestr, file=sys.stderr)
        if msg:
            self.assertIn(msg, capturestr)
        if regex:
            self.assertRegex(capturestr, regex)


class TestSimpleCases(Base):
    def test_simple(self):
        PARAMETERS = [
            (str_func, ["foo"], {"foo": "foo"}),
            (int_func, ["1"], {"one": 1}),
            (float_func, ["3.14"], {"pi": 3.14}),
            (float_func, ["314e-2"], {"pi": 3.14}),
            (path_func, ["/etc"], {"etc": pathlib.Path("/etc")}),
            (no_annotation_func, ["foo"], {"foo": "foo"}),
        ]

        for param in PARAMETERS:
            with self.subTest(param=param):
                (function, input, result) = param
                parser = clargs.create_parser(function)
                args = parser.parse_args(input)
                self.assertEqual(vars(args), {"_clargs_func_": function, **result})
                self.assertEqual(clargs.run(args), "SUCCESS")

    def test_fail(self):
        PARAMETERS = [
            (str_func, [], "the following arguments are required: foo"),
            (int_func, ["a"], "invalid int value: 'a'"),
            (no_annotation_func, [], "the following arguments are required: foo"),
            (path_func, [], "the following arguments are required: etc"),
        ]
        for param in PARAMETERS:
            with self.subTest(param=param):
                (function, input, expected_error) = param
                parser = clargs.create_parser(function)
                with self.assertExit(msg=expected_error):
                    parser.parse_args(input)

    def test_negative_float_without_e(self):
        parser = clargs.create_parser(float_func)
        args = parser.parse_args(["-3.14"])
        self.assertEqual(vars(args), {"_clargs_func_": float_func, "pi": -3.14})

    @unittest.expectedFailure  # seems to be an issue in argparse
    def test_negative_float_with_e(self):
        parser = clargs.create_parser(float_func)
        args = parser.parse_args(["-314e-2"])
        self.assertEqual(vars(args), {"_clargs_func_": float_func, "pi": -3.14})

    def test_default_value(self):
        def function(foo: str = "bar"):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": "bar"})

    def test_default_value_int(self):
        def function(three: int = 3):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "three": 3})

    def test_options(self):
        def function(foo: str, *, one: int):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["foo", "--one", "1"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "foo", "one": 1}
        )

    def test_options_with_default(self):
        def function(foo: str, *, one: int = 1):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["foo"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "foo", "one": 1}
        )
        args = parser.parse_args(["foo", "--one", "3"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "foo", "one": 3}
        )

    def test_param_name_with_dash(self):
        def function(*, my_number: int = 2):
            return my_number

        parser = clargs.create_parser(function)
        args = parser.parse_args(["--my-number", "3"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "my_number": 3})
        self.assertEqual(clargs.run(args), 3)
        with self.assertExit(msg="unrecognized arguments: --my_number 3"):
            args = parser.parse_args(["--my_number", "3"])

    def test_positional_param_name_with_underscore(self):
        def function(my_number: int = 2):
            return my_number

        parser = clargs.create_parser(function)
        args = parser.parse_args(["3"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "my_number": 3})
        self.assertEqual(clargs.run(args), 3)

    def test_positional_only_param(self):
        def function(mynumber: int = 2, /):
            return mynumber

        parser = clargs.create_parser(function)
        args = parser.parse_args(["3"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "mynumber": 3})
        self.assertEqual(clargs.run(args), 3)

    def test_mixed_params(self):
        def function(a: int, /, b: int, *, c: int):
            return a + b + c

        parser = clargs.create_parser(function)
        args = parser.parse_args(["3", "5", "--c", "7"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "a": 3, "b": 5, "c": 7}
        )
        self.assertEqual(clargs.run(args), 15)


class TestBooleans(Base):
    def test_boolean(self):
        def function(flag: bool):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["YES"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["NO"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": False})
        with self.assertExit(msg="invalid parse_bool value: 'maybe'"):
            parser.parse_args(["maybe"])

    def test_boolean_as_flag(self):
        def function(*, flag: bool):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["--flag", "YES"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["-f", "YES"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["--flag", "NO"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": False})
        with self.assertExit(msg="invalid parse_bool value: 'maybe'"):
            parser.parse_args(["--flag", "maybe"])

    def test_boolean_as_flag_without_value(self):
        def function(*, flag: bool):
            pass

        parser = clargs.create_parser(function)
        with self.assertExit(msg="expected one argument"):
            parser.parse_args(["--flag"])


class TestFlags(Base):
    def test_flags_default_false(self):
        def function(*, flag: clargs.Flag = False):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": False})
        args = parser.parse_args(["--flag"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["--no-flag"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": False})

    def test_flags_default_true(self):
        def function(*, flag: clargs.Flag = True):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["--flag"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["--no-flag"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": False})
        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})

    def test_flags_no_default(self):
        def function(*, flag: clargs.Flag):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["--flag"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["--no-flag"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": False})
        parser = clargs.create_parser(function)
        with self.assertExit(
            msg="the following arguments are required: " "--flag/--no-flag/-f"
        ):
            args = parser.parse_args([])

    def test_positional(self):
        def function(flag: clargs.Flag = True):
            pass

        with self.assertRaisesRegex(clargs.GetArgsFromTypeException, "Flag error"):
            clargs.create_parser(function)


class TestOptional(Base):
    def test_optional_str(self):
        def function(foo: t.Optional[str] = None):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": None})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": "bar"})

    def test_implicit_optional(self):
        def function(foo: str = None):  # type: ignore
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": None})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": "bar"})

    def test_union_str_none(self):
        def function(foo: str | None = None):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": None})
        args = parser.parse_args(["bar"])

    def test_union_none_str(self):
        def function(foo: None | str = None):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": None})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": "bar"})

    def test_optional_int(self):
        def function(number: t.Optional[int] = None):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "number": None})
        args = parser.parse_args(["1"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "number": 1})


class TestList(Base):
    def test_list_str(self):
        def function(foos: t.List[str]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["bar1", "bar2"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foos": ["bar1", "bar2"]}
        )
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foos": []})

    def test_list_int(self):
        def function(numbers: t.List[int]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["1", "2"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": [1, 2]})
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": []})

    def test_list_int_flag(self):
        def function(foo: str, *, numbers: list[int]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["bar", "--numbers", "1", "2"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "bar", "numbers": [1, 2]}
        )
        args = parser.parse_args(["bar", "--numbers"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "bar", "numbers": []}
        )
        args = parser.parse_args(
            ["bar", "--numbers", "1", "2", "--numbers", "3", "--numbers", "4", "5"]
        )
        self.assertEqual(
            vars(args),
            {"_clargs_func_": function, "foo": "bar", "numbers": [1, 2, 3, 4, 5]},
        )

    def test_list_int_flag_with_default(self):
        def function(foo: str, *, numbers: list[int] = []):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["bar", "--numbers", "1", "2"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "bar", "numbers": [1, 2]}
        )
        args = parser.parse_args(["bar", "--numbers"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "bar", "numbers": []}
        )
        args = parser.parse_args(
            ["bar", "--numbers", "1", "2", "--numbers", "3", "--numbers", "4", "5"]
        )
        self.assertEqual(
            vars(args),
            {"_clargs_func_": function, "foo": "bar", "numbers": [1, 2, 3, 4, 5]},
        )

    def test_list_int_literal(self):
        def function(numbers: t.List[t.Literal[1, 2, 3, 5, 7, 11]]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["1", "2", "11"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": [1, 2, 11]})
        with self.assertExit(msg="invalid choice: 4 (choose from 1, 2, 3, 5, 7, 11)"):
            parser.parse_args(["4"])
        with self.assertExit(msg="invalid choice: 4 (choose from 1, 2, 3, 5, 7, 11)"):
            parser.parse_args(["1", "2", "4"])
        with self.assertExit(msg="invalid choice: 4 (choose from 1, 2, 3, 5, 7, 11)"):
            parser.parse_args(["1", "2", "4", "11"])

    # seems to be an issue in argparse, fixed in 3.12
    @expectedFailureIf(sys.version_info < (3, 12))
    def test_list_int_literal_empty_list(self):
        def function(numbers: t.List[t.Literal[1, 2, 3, 5, 7, 11]]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": []})

    def test_list_bool(self):
        def function(bools: t.List[bool]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["yes", "no", "true", "False"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "bools": [True, False, True, False]}
        )

    def test_list_str_options(self):
        def function(*, numbers: t.List[int]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["--numbers", "1", "2"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": [1, 2]})
        args = parser.parse_args(["--numbers"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": []})
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": None})

    def test_list_int_minimal_one(self):
        def function(numbers: t.Annotated[t.List[int], clargs.extra_info(nargs="+")]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["1", "2"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "numbers": [1, 2]})
        with self.assertExit(msg="the following arguments are required: numbers"):
            parser.parse_args([])


class TestLiteral(Base):
    def test_string_literal(self):
        def function(foobar: t.Literal["foo", "bar", "baz"]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["foo"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foobar": "foo"})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foobar": "bar"})
        with self.assertExit(
            msg="invalid choice: 'foobar' " "(choose from 'foo', 'bar', 'baz'"
        ):
            parser.parse_args(["foobar"])

    def test_int_literal(self):
        def function(prime: t.Literal[1, 2, 3, 5, 7, 11]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["1"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "prime": 1})
        args = parser.parse_args(["11"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "prime": 11})
        with self.assertExit(msg="invalid choice: 4 (choose from 1, 2, 3, 5, 7, 11)"):
            parser.parse_args(["4"])


class TestCount(Base):
    def test_count(self):
        def function(*, flag: clargs.Count):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": 1})
        args = parser.parse_args(["-f"] * 5)
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": 5})

    def test_count_zero(self):
        def function(*, flag: clargs.Count):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": 0})

    # default gets overwritten (I mean, why would you want this anyways)
    @unittest.expectedFailure
    def test_count_other_default(self):
        def function(*, flag: clargs.Count = 3):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": 3})
        args = parser.parse_args(["--flag"] * 3)
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": 6})

    def test_count_positional(self):
        def function(flag: clargs.Count):
            pass

        with self.assertRaisesRegex(
            TypeError, "'required' is an invalid argument for positionals"
        ):
            clargs.create_parser(function)


class TestSettings(Base):
    def test_generate_short_flags(self):
        def function(*, flag: bool = False):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["-f", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})

        clargs_obj = clargs.Clargs(clargs.Settings(generate_short_flags=False))
        parser = clargs_obj.create_parser(function)
        with self.assertExit(msg="unrecognized arguments: -f yes"):
            parser.parse_args(["-f", "yes"])

    def test_generate_alternate_flags(self):
        def function(*, flag: bool = False):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["-f", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["--flag", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})

        clargs_obj = clargs.Clargs(
            clargs.Settings(flag_prefix="++", short_flag_prefix="+")
        )

        parser = clargs_obj.create_parser(function)
        with self.assertExit(msg="unrecognized arguments: -f yes"):
            parser.parse_args(["-f", "yes"])
        with self.assertExit(msg="unrecognized arguments: --flag yes"):
            parser.parse_args(["--flag", "yes"])
        args = parser.parse_args(["+f", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["++flag", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})

    def test_generate_windows_flags(self):
        def function(*, flag: bool = False):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["-f", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["--flag", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})

        clargs_obj = clargs.Clargs(
            clargs.Settings(flag_prefix="/", generate_short_flags=False)
        )

        parser = clargs_obj.create_parser(function)
        with self.assertExit(msg="unrecognized arguments: -f yes"):
            parser.parse_args(["-f", "yes"])
        with self.assertExit(msg="unrecognized arguments: --flag yes"):
            parser.parse_args(["--flag", "yes"])
        args = parser.parse_args(["/flag", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["/fla", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})
        args = parser.parse_args(["/f", "yes"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "flag": True})

    def test_settings_flag(self):
        def function(foo: str, /, bar: str, *, sasa: str):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["foo", "bar", "-s", "sasa"])
        self.assertEqual(
            vars(args),
            {"_clargs_func_": function, "foo": "foo", "bar": "bar", "sasa": "sasa"},
        )

        clargs_obj = clargs.Clargs(
            clargs.Settings(positional_and_kw_args_become="flag")
        )
        parser = clargs_obj.create_parser(function)
        args = parser.parse_args(["foo", "--bar", "bar", "-s", "sasa"])
        self.assertEqual(
            vars(args),
            {"_clargs_func_": function, "foo": "foo", "bar": "bar", "sasa": "sasa"},
        )

    def test_settings_flag_if_has_default(self):
        def function(foo: str, bar: str = "baz"):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["foo", "bar"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "foo", "bar": "bar"}
        )

        clargs_obj = clargs.Clargs(
            clargs.Settings(positional_and_kw_args_become="flag_if_default")
        )
        parser = clargs_obj.create_parser(function)
        args = parser.parse_args(["foo", "--bar", "bar"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "foo": "foo", "bar": "bar"}
        )

    def test_settings_no_dash_replacement(self):
        def function(*, my_number: int):
            return my_number

        parser = clargs.create_parser(function)
        args = parser.parse_args(["--my-number", "3"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "my_number": 3})

        clargs_obj = clargs.Clargs(clargs.Settings(replace_underscore_with_dash=False))
        parser = clargs_obj.create_parser(function)
        args = parser.parse_args(["--my_number", "3"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "my_number": 3})


class TestListOfOne(Base):
    def test_list(self):
        def function(foo: clargs.ListOfAtLeastOne[float]):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["2.5", "3"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "foo": [2.5, 3]})

    def test_list_with_zero_items(self):
        def function(foo: clargs.ListOfAtLeastOne[float]):
            pass

        parser = clargs.create_parser(function)
        with self.assertExit(msg="the following arguments are required: foo"):
            parser.parse_args([])


class TestSubParsers(Base):
    def test_two_groups(self):
        import argparse

        def do_sum(terms: list[int]) -> int:
            return sum(terms)

        def do_product(factors: list[float]) -> float:
            import math

            return math.prod(factors)

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(required=True)
        clargs.add_subparser(subparsers, do_sum)
        clargs.add_subparser(subparsers, do_product)

        args = parser.parse_args(["do-sum", "2", "56", "-4"])
        self.assertEqual(clargs.run(args), 54)

        args = parser.parse_args(["do-product", "2", "3.1415", "-1.3"])
        self.assertEqual(clargs.run(args), 2 * 3.1415 * -1.3)


class TestFlagShortening(Base):
    def test_multiple_flags_with_same_start_letter(self):
        def function(*, flag1: int = 1, flag2: int = 2):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["-f", "3"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "flag1": 3, "flag2": 2}
        )

    def test_multiple_flags_with_shortcode_overridden_later(self):
        def function(
            *,
            flag1: int = 1,
            flag2: t.Annotated[int, clargs.extra_info(aliases=["-f"])] = 2,
        ):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["-f", "3"])
        self.assertEqual(
            vars(args), {"_clargs_func_": function, "flag1": 1, "flag2": 3}
        )
