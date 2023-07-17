"""
Examples:

>>> python examples/4_parse_groups.py --help (returncode: 0)
usage: 4_parse_groups.py [-h] {count,math} ...

positional arguments:
  {count,math}
    count       Counts from 1 to given number (default = 10)
    math        Does math on the list of numbers, based on the first term

options:
  -h, --help    show this help message and exit

>>> python examples/4_parse_groups.py count --help (returncode: 0)
usage: 4_parse_groups.py count [-h] [--shout | --no-shout | -s]
                               {Human,Horse,Sheep} {Humans,Horses,Sheep}
                               [maxitems ...]

positional arguments:
  {Human,Horse,Sheep}   The singular form of the thing to count
  {Humans,Horses,Sheep}
                        The plural form of the thing to count
  maxitems              A list of numbers to count to

options:
  -h, --help            show this help message and exit
  --shout, --no-shout, -s
                        If True, will convert all expressions to capitals

>>> python examples/4_parse_groups.py math --help (returncode: 0)
usage: 4_parse_groups.py math [-h] [--round-to-int | --no-round-to-int | -r]
                              [--absolute-value | --no-absolute-value | -a]
                              {add,mul,sub,truediv} numbers [numbers ...]

positional arguments:
  {add,mul,sub,truediv}
                        Add, Multiply, Subtract or Divide
  numbers               List of numbers to operate on

options:
  -h, --help            show this help message and exit
  --round-to-int, --no-round-to-int, -r
                        If True, the result will be round to closest int
  --absolute-value, --no-absolute-value, -a
                        If True, the result will be made positive

>>> python examples/4_parse_groups.py count Human Humans 2 (returncode: 0)
maxitems: [2]
1 Human
2 Humans

>>> python examples/4_parse_groups.py count Human Humans # normal list may have size 0 (returncode: 0)
maxitems: []

>>> python examples/4_parse_groups.py math add 10 20 6 3 2 1 --round # argparse allows you to shorten parameters (returncode: 0)
Result: 42

>>> python examples/4_parse_groups.py math sub 10 20 6 3 2 1 --abs (returncode: 0)
Result: 22.0

>>> python examples/4_parse_groups.py math truediv 50 -3 (returncode: 0)
Result: -16.666666666666668

>>> python examples/4_parse_groups.py math truediv 50 -3 -ra # -r is --round-to-int and -a is --absolute-value; you can combine them into -ra (returncode: 0)
Result: 17

>>> python examples/4_parse_groups.py math add # Number is required now since type is ListOfAtLeastOne (returncode: 2)
usage: 4_parse_groups.py math [-h] [--round-to-int | --no-round-to-int | -r]
                              [--absolute-value | --no-absolute-value | -a]
                              {add,mul,sub,truediv} numbers [numbers ...]
4_parse_groups.py math: error: the following arguments are required: numbers

"""
import argparse
import clargs
import operator as mod_operator
import typing as t


def count(
    # Limit the choices for singular and plural
    singular: t.Literal["Human", "Horse", "Sheep"],
    plural: t.Literal["Humans", "Horses", "Sheep"],
    # make maxitems a list. Note that the
    # argparse.ArgumentDefaultsHelpFormatter has a problem
    # with specifying the default return type
    maxitems: list[int],
    *,
    # By giving shout a default value of None, it can switch between
    # three states now (--shout / --no-shout or nothing).
    shout: t.Optional[clargs.Flag] = None,
):
    """
    Counts from 1 to given number (default = 10)

    This text should not appear

    @param singular: The singular form of the thing to count
    @param plural: The plural form of the thing to count
    @param maxitems: A list of numbers to count to
    @param shout: If True, will convert all expressions to capitals
    """
    print(f"maxitems: {maxitems}")
    for maxitem in maxitems:
        for i in range(maxitem):
            text = f"{i + 1} {singular if i == 0 else plural}"
            if shout is True:
                text = text.upper()
            if shout is False:
                text = text.lower()
            print(text)


def math(
    operator: t.Literal["add", "mul", "sub", "truediv"],
    # This helper class defines a list of size 1 or more
    numbers: clargs.ListOfAtLeastOne[float],
    *,
    # note that underscores will become dashes in cli
    round_to_int: clargs.Flag = False,
    absolute_value: clargs.Flag = False,
):
    """
    Does math on the list of numbers, based on the first term

    @param operator: Add, Multiply, Subtract or Divide
    @param numbers: List of numbers to operate on
    @param round_to_int: If True, the result will be round to closest int
    @param absolute_value: If True, the result will be made positive
    """
    value = numbers[0]
    chosen_operator = getattr(mod_operator, operator)
    for n in numbers[1:]:
        value = chosen_operator(value, n)
    if round_to_int:
        value = int(round(value))
    if absolute_value:
        value = abs(value)
    print(f"Result: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers()
    clargs.add_subparser(subparsers, count)
    clargs.add_subparser(subparsers, math)
    clargs.run(parser.parse_args())
