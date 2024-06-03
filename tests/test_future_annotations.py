from __future__ import annotations
import clargs
import pathlib
from .test_simple import Base


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


class TestFutureAnnotationsCases(Base):
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
