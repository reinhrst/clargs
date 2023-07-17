"""
Examples:

>>> python examples/3_list.py --help (returncode: 0)
usage: 3_list.py [-h] [--shout | --no-shout | -s]
                 {Human,Horse,Sheep} {Humans,Horses,Sheep} [maxitems ...]

Counts from 1 to given number (default = 10)

positional arguments:
  {Human,Horse,Sheep}   The singular form of the thing to count
  {Humans,Horses,Sheep}
                        The plural form of the thing to count
  maxitems              A list of numbers to count to (default: None)

options:
  -h, --help            show this help message and exit
  --shout, --no-shout, -s
                        If True, will convert all expressions to capitals
                        (default: None)

>>> python examples/3_list.py Human Sheep 3 5 3 # No requirement to take the same items (returncode: 0)
maxitems: [3, 5, 3]
1 Human
2 Sheep
3 Sheep
1 Human
2 Sheep
3 Sheep
4 Sheep
5 Sheep
1 Human
2 Sheep
3 Sheep

>>> python examples/3_list.py Human Humans 2 2 --shout (returncode: 0)
maxitems: [2, 2]
1 HUMAN
2 HUMANS
1 HUMAN
2 HUMANS

>>> python examples/3_list.py Human Humans 2 2 --no-shout (returncode: 0)
maxitems: [2, 2]
1 human
2 humans
1 human
2 humans

>>> python examples/3_list.py Human Humans (returncode: 0)
maxitems: []

>>> python examples/3_list.py Alien Aliens 2 2 --no-shout (returncode: 2)
usage: 3_list.py [-h] [--shout | --no-shout | -s]
                 {Human,Horse,Sheep} {Humans,Horses,Sheep} [maxitems ...]
3_list.py: error: argument singular: invalid choice: 'Alien' (choose from 'Human', 'Horse', 'Sheep')

"""
import argparse
import clargs
import typing as t


def count(
    # Limit the choices for singular and plural
    singular: t.Literal["Human", "Horse", "Sheep"],
    plural: t.Literal["Humans", "Horses", "Sheep"],
    # make maxitems a list. Note that the
    # argparse.ArgumentDefaultsHelpFormatter has a problem
    # with specifying the default return type
    # Also note that empty list is allowed
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


if __name__ == "__main__":
    parser = clargs.create_parser(count)
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    clargs.run(parser.parse_args())
