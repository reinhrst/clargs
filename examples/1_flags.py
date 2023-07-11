import argize


def count(
    singular: str,
    plural: str,
    maxitems: int = 10,
    *,
    # Type argize.Flag is an alias for bool, which allows --shout/--no-shout
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
    argize.create_parser_and_run(count)
