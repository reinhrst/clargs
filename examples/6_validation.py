"""
Examples:

>>> python examples/6_validation.py 2 (returncode: 0)
The given even number is: 2

>>> python examples/6_validation.py -2 (returncode: 0)
The given even number is: -2

>>> python examples/6_validation.py 1 (returncode: 2)
usage: 6_validation.py [-h] number
6_validation.py: error: argument number: invalid validate value: '1'

"""
import clargs
import typing as t


def print_even_number(
    number: t.Annotated[
        int,
        clargs.extra_info(
            validate=lambda n: n % 2 == 0,
        ),
    ]
):
    """
    Prints a number

    @param number: An even number
    """
    print(f"The given even number is: {number}")


if __name__ == "__main__":
    clargs.create_parser_and_run(print_even_number)
