import argize
import unittest
import pathlib
import typing as t
import logging

logging.basicConfig(level=logging.DEBUG)


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


class TestSimpleCases(unittest.TestCase):
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
                print(param)
                (function, input, result) = param
                parser = argize.create_parser(function)
                args = parser.parse_args(input)
                self.assertEqual(
                    vars(args), {"_argize_func_": function, **result})
                self.assertEqual(argize.run(args), "SUCCESS")

    def test_fail(self):
        PARAMETERS = [
            (str_func, [], {"foo": "foo"}),
            (int_func, ["a"], {"one": 1}),
            (no_annotation_func, [], {"foo": "foo"}),
            (path_func, [], {"etc": pathlib.Path("/etc")}),
        ]
        for param in PARAMETERS:
            with self.subTest(param=param):
                (function, input, result) = param
                parser = argize.create_parser(function)
                with self.assertRaises(SystemExit):
                    parser.parse_args(input)

    def test_default_value(self):
        def function(foo: str = "bar"):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": "bar"})

    def test_default_value_int(self):
        def function(three: int = 3):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_argize_func_": function, "three": 3})

    def test_options(self):
        def function(foo: str, *, one: int):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["foo", "--one", "1"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "foo": "foo", "one": 1})

    def test_options_with_default(self):
        def function(foo: str, *, one: int = 1):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["foo"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "foo": "foo", "one": 1})
        args = parser.parse_args(["foo", "--one", "3"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "foo": "foo", "one": 3})

    def test_param_name_with_dash(self):
        def function(*, my_number: int):
            return my_number

        parser = argize.create_parser(function)
        args = parser.parse_args(["--my-number", "3"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "my_number": 3})
        self.assertEqual(argize.run(args), 3)
        with self.assertRaises(SystemExit):
            args = parser.parse_args(["--my_number", "3"])


class TestBooleans(unittest.TestCase):
    def test_boolean(self):
        def function(flag: bool):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["YES"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["NO"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})
        with self.assertRaises(SystemExit):
            parser.parse_args(["maybe"])

    def test_boolean_as_flag(self):
        def function(*, flag: bool):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["--flag", "YES"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["-f", "YES"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["--flag", "NO"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})
        with self.assertRaises(SystemExit):
            parser.parse_args(["--flag", "maybe"])


class TestFlags(unittest.TestCase):
    def test_flags_default_false(self):
        def function(*, flag: argize.Flag = False):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})
        args = parser.parse_args(["--flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["--no-flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})

    def test_flags_default_true(self):
        def function(*, flag: argize.Flag = True):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["--flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["--no-flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})
        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})

    def test_flags_no_default(self):
        def function(*, flag: argize.Flag):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["--flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["--no-flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})
        parser = argize.create_parser(function)
        with self.assertRaises(SystemExit):
            args = parser.parse_args([])

    def test_positional(self):
        def function(flag: argize.Flag = True):
            pass

        with self.assertRaisesRegex(
                argize.GetArgsFromTypeException, "Flag error"):
            argize.create_parser(function)


class TestOptional(unittest.TestCase):
    def test_optional_str(self):
        def function(foo: t.Optional[str] = None):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": None})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": "bar"})

    def test_implicit_optional(self):
        def function(foo: str = None):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": None})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": "bar"})

    def test_union_str_none(self):
        def function(foo: str | None = None):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": None})
        args = parser.parse_args(["bar"])

    def test_union_none_str(self):
        def function(foo: None | str = None):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": None})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {"_argize_func_": function, "foo": "bar"})

    def test_optional_int(self):
        def function(number: t.Optional[int] = None):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "number": None})
        args = parser.parse_args(["1"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "number": 1})


class TestList(unittest.TestCase):
    def test_list_str(self):
        def function(foos: t.List[str]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["bar1", "bar2"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "foos": ["bar1", "bar2"]})
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "foos": []})

    def test_list_int(self):
        def function(numbers: t.List[int]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["1", "2"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": [1, 2]})
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": []})

    def test_list_int_literal(self):
        def function(numbers: t.List[t.Literal[1, 2, 3, 5, 7, 11]]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["1", "2", "11"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": [1, 2, 11]})
        with self.assertRaises(SystemExit):
            parser.parse_args(["4"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["1", "2", "4"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["1", "2", "4", "11"])

    @unittest.expectedFailure  # seems to be an issue in argparse
    def test_list_int_literal_empty_list(self):
        def function(numbers: t.List[t.Literal[1, 2, 3, 5, 7, 11]]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": []})

    def test_list_bool(self):
        def function(bools: t.List[bool]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["yes", "no", "true", "False"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "bools": [True, False, True, False]})

    def test_list_str_options(self):
        def function(*, numbers: t.List[int]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["--numbers", "1", "2"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": [1, 2]})
        args = parser.parse_args(["--numbers"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": []})
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": None})

    def test_list_int_minimal_one(self):
        def function(
                numbers: t.Annotated[
                    t.List[int], argize.extra_info(nargs="+")]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["1", "2"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": [1, 2]})
        with self.assertRaises(SystemExit):
            parser.parse_args([])


class TestLiteral(unittest.TestCase):
    def test_string_literal(self):
        def function(foobar: t.Literal["foo", "bar", "baz"]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["foo"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "foobar": "foo"})
        args = parser.parse_args(["bar"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "foobar": "bar"})
        with self.assertRaises(SystemExit):
            parser.parse_args(["foobar"])

    def test_int_literal(self):
        def function(prime: t.Literal[1, 2, 3, 5, 7, 11]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["1"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "prime": 1})
        args = parser.parse_args(["11"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "prime": 11})
        with self.assertRaises(SystemExit):
            parser.parse_args(["4"])


class TestCount(unittest.TestCase):
    def test_count(self):
        def function(*, flag: argize.Count):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["-f"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": 1})
        args = parser.parse_args(["-f"] * 5)
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": 5})

    def test_count_zero(self):
        def function(*, flag: argize.Count):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": 0})

    # default gets overwritten (I mean, why would you want this anyways)
    @unittest.expectedFailure
    def test_count_other_default(self):
        def function(*, flag: argize.Count = 3):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": 3})
        args = parser.parse_args(["--flag"] * 3)
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": 6})

    def test_count_positional(self):
        # Not really sure this makes sense, but it's how it works
        def function(flag: argize.Count):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": 1})
