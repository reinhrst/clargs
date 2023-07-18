"""
Examples:

>>> python examples/5_logging.py --help (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x100d7a5c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x100d7a5c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x100d7a5c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
usage: 5_logging.py [-h] {count,math} ...

positional arguments:
  {count,math}
    count       Counts from 1 to given number (default = 10)
    math        Does math on the list of numbers, based on the first term

options:
  -h, --help    show this help message and exit

>>> python examples/5_logging.py count --help (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1011725c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1011725c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1011725c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
usage: 5_logging.py count [-h] [--shout | --no-shout | -s]
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

>>> python examples/5_logging.py math --help (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102d8a5c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102d8a5c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102d8a5c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
usage: 5_logging.py math [-h] [--round-to-int | --no-round-to-int | -r]
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

>>> python examples/5_logging.py count Human Humans 2 (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102c025c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102c025c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102c025c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
DEBUG:clargs:Received parsed args Namespace(singular='Human', plural='Humans', maxitems=[2], shout=None, _clargs_func_=<function count at 0x10243e020>)
maxitems: [2]
1 Human
2 Humans

>>> python examples/5_logging.py count Human Humans # normal list may have size 0 (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x10386e5c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x10386e5c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x10386e5c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
DEBUG:clargs:Received parsed args Namespace(singular='Human', plural='Humans', maxitems=[], shout=None, _clargs_func_=<function count at 0x1030aa020>)
maxitems: []

>>> python examples/5_logging.py math add 10 20 6 3 2 1 --round # argparse allows you to shorten parameters (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x103a125c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x103a125c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x103a125c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
DEBUG:clargs:Received parsed args Namespace(operator='add', numbers=[10.0, 20.0, 6.0, 3.0, 2.0, 1.0], round_to_int=True, absolute_value=False, _clargs_func_=<function math at 0x1034a9300>)
Result: 42

>>> python examples/5_logging.py math sub 10 20 6 3 2 1 --abs (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1037ba5c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1037ba5c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1037ba5c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
DEBUG:clargs:Received parsed args Namespace(operator='sub', numbers=[10.0, 20.0, 6.0, 3.0, 2.0, 1.0], round_to_int=False, absolute_value=True, _clargs_func_=<function math at 0x103251300>)
Result: 22.0

>>> python examples/5_logging.py math truediv 50 -3 (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102e3e5c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102e3e5c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x102e3e5c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
DEBUG:clargs:Received parsed args Namespace(operator='truediv', numbers=[50.0, -3.0], round_to_int=False, absolute_value=False, _clargs_func_=<function math at 0x1028d5300>)
Result: -16.666666666666668

>>> python examples/5_logging.py math truediv 50 -3 -ra # -r is --round-to-int and -a is --absolute-value; you can combine them into -ra (returncode: 0)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1059d25c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1059d25c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1059d25c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
DEBUG:clargs:Received parsed args Namespace(operator='truediv', numbers=[50.0, -3.0], round_to_int=True, absolute_value=True, _clargs_func_=<function math at 0x105469300>)
Result: 17

>>> python examples/5_logging.py math add # Number is required now since type is ListOfAtLeastOne (returncode: 2)
DEBUG:clargs:Adding (['singular'], {'choices': ('Human', 'Horse', 'Sheep'), 'help': 'The singular form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['plural'], {'choices': ('Humans', 'Horses', 'Sheep'), 'help': 'The plural form of the thing to count', 'type': <class 'str'>})
DEBUG:clargs:Adding (['maxitems'], {'action': 'extend', 'help': 'A list of numbers to count to', 'nargs': '*', 'type': <class 'int'>})
DEBUG:clargs:Adding (['--shout', '-s'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1032de5c0>, 'default': None, 'help': 'If True, will convert all expressions to capitals', 'required': False})
DEBUG:clargs:Adding (['operator'], {'choices': ('add', 'mul', 'sub', 'truediv'), 'help': 'Add, Multiply, Subtract or Divide', 'type': <class 'str'>})
DEBUG:clargs:Adding (['numbers'], {'action': 'extend', 'help': 'List of numbers to operate on', 'nargs': '+', 'type': <class 'float'>})
DEBUG:clargs:Adding (['--round-to-int', '-r'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1032de5c0>, 'default': False, 'help': 'If True, the result will be round to closest int', 'required': False})
DEBUG:clargs:Adding (['--absolute-value', '-a'], {'action': <function BooleanOptionalActionWitoutImplicitDefault at 0x1032de5c0>, 'default': False, 'help': 'If True, the result will be made positive', 'required': False})
usage: 5_logging.py math [-h] [--round-to-int | --no-round-to-int | -r]
                         [--absolute-value | --no-absolute-value | -a]
                         {add,mul,sub,truediv} numbers [numbers ...]
5_logging.py math: error: the following arguments are required: numbers

"""
import argparse
import clargs
import operator as mod_operator
import logging
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
    # By switching on debug level logging, you see exactly the parameters given to `argparse`'s `add_argument`, and the result of the parsing
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers()
    clargs.add_subparser(subparsers, count)
    clargs.add_subparser(subparsers, math)
    clargs.run(parser.parse_args())
