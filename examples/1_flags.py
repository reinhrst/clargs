"""
Examples:

>>> python examples/1_flags.py --help (returncode: 0)
usage: 1_flags.py [-h] [--shout | --no-shout | -s] singular plural [maxitems]

Counts from 1 to given number (default = 10)

positional arguments:
  singular              The singular form of the thing to count
  plural                The plural form of the thing to count
  maxitems              The number to count to

options:
  -h, --help            show this help message and exit
  --shout, --no-shout, -s
                        If True, will convert all expressions to capitals

>>> python examples/1_flags.py Human (returncode: 2)
usage: 1_flags.py [-h] [--shout | --no-shout | -s] singular plural [maxitems]
1_flags.py: error: the following arguments are required: plural

>>> python examples/1_flags.py Human Humans (returncode: 0)
1 Human
2 Humans
3 Humans
4 Humans
5 Humans
6 Humans
7 Humans
8 Humans
9 Humans
10 Humans

>>> python examples/1_flags.py Human Humans 5 --shout (returncode: 0)
1 HUMAN
2 HUMANS
3 HUMANS
4 HUMANS
5 HUMANS

>>> python examples/1_flags.py Human Humans 5 --no-shout (returncode: 0)
1 Human
2 Humans
3 Humans
4 Humans
5 Humans

>>> python examples/1_flags.py Human Humans 5 --shout=yes (returncode: 2)
usage: 1_flags.py [-h] [--shout | --no-shout | -s] singular plural [maxitems]
1_flags.py: error: argument --shout/--no-shout/-s: ignored explicit argument 'yes'

"""
import clargs


def count(
    singular: str,
    plural: str,
    maxitems: int = 10,
    *,
    # Type clargs.Flag is an alias for bool, which allows --shout/--no-shout
    shout: clargs.Flag = False,
):
    """
    Counts from 1 to given number (default = 10)

    This text should not appear

    @param singular: The singular form of the thing to count
    @param plural: The plural form of the thing to count
    @param maxitems: The number to count to
    @param shout: If True, will convert all expressions to capitals
    """
    for i in range(maxitems):
        text = f"{i + 1} {singular if i == 0 else plural}"
        if shout:
            text = text.upper()
        print(text)


if __name__ == "__main__":
    clargs.create_parser_and_run(count)
