import argparse
import argize


def count(
    singular: str,
    plural: str,
    maxitems: int = 10,
    *,
    shout: argize.Flag = False,
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
    parser = argize.create_parser(count)
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    argize.run(parser.parse_args())
