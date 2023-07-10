# Argize

The goal of the `argize` package is to create commandline interfaces from function signatures.

- With a single line, an existing function is turned into a command line program
- However it also has the flexibility to be the command line interface of a finished product
- Explicit goal is **Don't Repeat Yourself**. All information is in a single spot (where you define the function)
- Pure python and no dependencies (except for running test)
- Support for `int`, `float`, `bool`, `pathlib.Path`, `list` and `typing.Literal` built-in (more coming)
- Support for flags (`--foo/--no-foo`)
- Automatic underscore-to-dash conversion (`foo_bar` becomes `--foo-bar`), and creation of short flags (`--foo-bar` and `-f` are both supported)
- Type of a parameter is set through [PEP 484][2]-style type hints
- Defaults are taken from the function signature
- Based on the built-in `argparse` module


## Example

Quick example ([see here for more examples][3]) (it just works out of the box!):
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
    argize.create_parser_and_run(count)
```

```console
> python main.py --help
usage: main.py [-h] [--shout [SHOUT]] singular plural [maxitems]

Counts from 1 to given number (default = 10)

positional arguments:
  singular
  plural
  maxitems

options:
  -h, --help            show this help message and exit
  --shout [SHOUT], -s [SHOUT]

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
> python main.py bottle bottles 5 --shout=yes
1 BOTTLE
2 BOTTLES
3 BOTTLES
4 BOTTLES
5 BOTTLES
```

## Supported types

The type of the parameter (given through a type-hint) determines what the input is parsed at.
If no type-hint is given, `str` is assumed.

#### `str`, `int`, `float`, `pathlib.Path`

These types just call the constructor on the string (e.g. `python main.py --input-file /tmp/myfile.txt --repeat 5` will assign `pathlib.Path("/tmp/myfile.txt")` to `input_file` and `int("5")` to `repeat` (assuming a function signature like: `def run(*, input_file: pathlib.Path, repeat: int)`).

#### `bool`

Booleans need some special work internally (since `bool("False") == True`). Any parameter of type `bool` will accept `Yes`, `No`, `True` and `False` (case-insensitive) as values.
Booleans can also be made `Flag`s, see below under "Extra Types".

#### `typing.Literal["foo", "bar", "baz"]`

Using `typing.Literal` parameters can be made that can only have certain values.
The type of the parameters can be any of the types above

#### `list[X]` or `typing.Sequence[X]`

Lists of items is supported (for all pf the above types). For instance a signature of `def sum(*, terms: typing.List[float]) -> float` means you can use `python sum.py --terms 1.2 4 -5`

#### `typing.Optional[X]` and `None | X`

`typing.Optional` or a union with `None` is ignored, so this won't affect the command line signature.


### Extra Types

In addition to normal types, the `argize` package defines some special types.

#### `argize.Flag`

Is an alias for `bool` (should be recognised by static type-checkers).
Creates `--foo/--no-foo` parameter pair to control booleans


#### `argize.Count`

Is an alias for `int` (should be recognised by static type-checkers).
Counts how often a parameter is present (mostly used in `--verbose --verbose --verbose` parameters)

### Custom Type

I hope to add types quickly in future versions.

In the meantime, any type not listed here will also work as long as an explicit conversion function is defined.


[1]: https://docs.python.org/3/library/typing.html#typing.Annotated
[2]: https://peps.python.org/pep-0484/
[3]: examples/
