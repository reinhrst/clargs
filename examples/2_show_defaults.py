"""
Examples:

>>> python examples/2_show_defaults.py --help # Notice the (default: 10) parts (returncode: 0)
usage: 2_show_defaults.py [-h] [--shout | --no-shout | -s]
                          singular plural [maxitems]

Counts from 1 to given number (default = 10)

positional arguments:
  singular              The singular form of the thing to count
  plural                The plural form of the thing to count
  maxitems              The number to count to (default: 10)

options:
  -h, --help            show this help message and exit
  --shout, --no-shout, -s
                        If True, will convert all expressions to capitals
                        (default: False)

"""
import argparse
import clargs


def count(
    singular: str,
    plural: str,
    maxitems: int = 10,
    *,
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
    # You can set a custom formatter_class for printing help
    # The argparse.ArgumentDefaultsHelpFormatter shows default values
    # in the help
    parser = clargs.create_parser(count)
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    clargs.run(parser.parse_args())
