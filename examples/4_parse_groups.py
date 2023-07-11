import argparse
import argize
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
    shout: t.Optional[argize.Flag] = None,
):
    """
    Counts from 1 to given number (default = 10)

    This text should not appear

    @param singular: The singular form of the thing to count
    @param plural: The plural form of the thing to count
    @param maxitems: A list of numbers to count to
    @param shout: If True, will convert all expressions to capitals
    """
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
    numbers: argize.ListOfAtLeastOne[float],
    *,
    # note that underscores will become dashes in cli
    round_to_int: argize.Flag = False,
    absolute_value: argize.Flag = False,
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
    argize.add_subparser(subparsers, count)
    argize.add_subparser(subparsers, math)
    argize.run(parser.parse_args())
