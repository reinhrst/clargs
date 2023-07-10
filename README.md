# Argize

The goal of the `argize` package is to quickly create commandline interfaces from function signatures.
Explicit goal is **Don't Repeat Yourself**, so that if you change a variable in the function signature, it will automatically appear as commandline option.
The module is pure-python and has no dependencies (except for running the tests).

- `argize` uses the built-in python `argparse` module under the hood (so you get all the `argparse` goodness)
- `argize` makes use of type hints on the function, in order to fill the arguments on `argparse`.
- All positional function arguments become positional parameters, keyword-only arguments become double-dash-flags.
- Support for default values and lists
- Support for boolean flags (both with `default=True` and `default=False`)

Quick example:
```python
import argize


def count(
    singular: str,
    plural: str,
    maxitems: int = 10,
    *,
    shout: bool = False,
):
    """Counts from 1 to given number (default = 10)"""
    for i in range(maxitems):
        text = f"{i + 1} {singular if i == 0 else plural}"
        if shout:
            text = text.upper()
        print(text)

if __name__ == "__main__":
    parser = argize.create_parser(count)
    argize.run(parser.parse_args())
```

```console
> python main.py --help
usage: main.py [-h] [--shout] singular plural [maxitems]

Counts from 1 to given number (default = 10)

positional arguments:
  singular
  plural
  maxitems

options:
  -h, --help  show this help message and exit
  --shout
> python main.py bottle bottles
1 bottle
2 bottles
3 bottles
4 bottles
5 bottles
6 bottles
7 bottles
8 bottles
9 bottles
10 bottles
> python main.py bottle bottles 5 --shout
1 BOTTLE
2 BOTTLES
3 BOTTLES
4 BOTTLES
5 BOTTLES
```

In the current (first) version, argize supports `str`, `int`, `float`, `pathlib.Path` as types.
When these types are given, the input in automatically converted into the correct type (other types need the user to specify the construction function).

Types may be optional (either using `t.Optional[str]`, or `str | None`), and lists are supported (`list[int]`) will get a list from the commandline (using `nargs="*"`).

Boolean values are a bit special.
Booleans are only allowed for keyword-only arguments, and always need a default value.
If the default is `False` (and the parameter name is `flag`), then using `--flag` the value is set to `True`.
However if the default is `True`, and the parameter name is `flag`, then a `--no-flag` is expected to set the value to `False`.

Using the magic of [`typing.Annotated`][1], additional parameters can be given to `argparse`.


[1]: https://docs.python.org/3/library/typing.html#typing.Annotated
