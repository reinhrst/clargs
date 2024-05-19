import clargs
import typing as t
from test_simple import Base


class TestValidationCases(Base):
    def test_validation(self):
        LessThanTenInt = t.Annotated[int, clargs.extra_info(validate=lambda n: n < 10)]

        def function(*, less_than_ten: LessThanTenInt):
            pass

        parser = clargs.create_parser(function)
        args = parser.parse_args(["--less-than-ten", "2"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "less_than_ten": 2})
        args = parser.parse_args(["--less-than-ten", "-2"])
        self.assertEqual(vars(args), {"_clargs_func_": function, "less_than_ten": -2})
        with self.assertExit(
            msg="argument --less-than-ten/-l: invalid int-validation value: '20'"
        ):
            parser.parse_args(["--less-than-ten", "20"])
