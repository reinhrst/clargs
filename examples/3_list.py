import argparse
import argize
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


if __name__ == "__main__":
    parser = argize.create_parser(count)
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    argize.run(parser.parse_args())
