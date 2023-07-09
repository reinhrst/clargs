import argparse
import argize
import unittest
import parameterized
import pathlib
import typing as t


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
    @parameterized.parameterized.expand([
        ("str", ["foo"], {"foo": "foo"}),
        ("int", ["1"], {"one": 1}),
        ("float", ["3.14"], {"pi": 3.14}),
        ("float", ["314e-2"], {"pi": 3.14}),
        ("no_annotation", ["foo"], {"foo": "foo"}),
        ("path", ["/etc"], {"etc": pathlib.Path("/etc")}),
        ])
    def test_simple(self, prefix, input, result):
        function = globals().get(f"{prefix}_func")
        parser = argize.create_parser(function)
        args = parser.parse_args(input)
        self.assertEqual(vars(args), {"_argize_func_": function, **result})
        self.assertEqual(argize.run(args), "SUCCESS")

    @parameterized.parameterized.expand([
        ("str", [], {"foo": "foo"}),
        ("int", ["a"], {"one": 1}),
        ("no_annotation", [], {"foo": "foo"}),
        ("path", [], {"etc": pathlib.Path("/etc")}),
        ])
    def test_fail(self, prefix, input, result):
        function = globals().get(f"{prefix}_func")
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


class TestBooleans(unittest.TestCase):
    def test_boolean_flags_default_false(self):
        def function(*, flag: bool = False):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})
        args = parser.parse_args(["--flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})

    def test_boolean_flags_default_true(self):
        def function(*, flag: bool = True):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args([])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": True})
        args = parser.parse_args(["--no-flag"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "flag": False})

    def test_boolean_flags_no_default(self):
        def function(*, flag: bool):
            pass

        with self.assertRaisesRegexp(
                argize.GetArgsFromTypeException,
                "Boolean types always need a default value"):
            argize.create_parser(function)

    def test_boolean_positional(self):
        def function(flag: bool = True):
            pass

        with self.assertRaisesRegexp(
                argize.GetArgsFromTypeException,
                "Boolean types can only be used in keyword-only arguments"):
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
                numbers: t.Annotated[t.List[int], argize.Params(nargs="+")]):
            pass

        parser = argize.create_parser(function)
        args = parser.parse_args(["1", "2"])
        self.assertEqual(vars(args), {
            "_argize_func_": function, "numbers": [1, 2]})
        with self.assertRaises(SystemExit):
            parser.parse_args([])
