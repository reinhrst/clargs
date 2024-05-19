# Clargs

The goal of the `clargs` package is to create commandline interfaces from function signatures.

- **Hit the ground running**: With a single line, an existing function is turned into a command line program
- **Extensible**: It is flexible enough to do everything that `argparse` does, and keeps you in control
- **No magic**: All the extension does is call commands in `argparse`; you can log and see these commands
- **Safe**: The built-in python `argparse` module does all the work, so safety guarantees from that module apply
- **Typing**: Parameter types are set as [PEP 484][2] type hints (e.g. `def foo(bar: int)`)
- **Standard**: By using `argparse`, you get standard behaviour such as long/short parameters, combine flags, help function
- **Don't repeat yourself**: Every parameter is defined (changed, added, removed) in one spot and only one spot, the function definition
- **Rich parameter types**: Support for `str`, `int`, `float`, `bool`, `pathlib.Path` and `typing.Literal` (multiple-choice values)
- **Richer parameter types**: In addition, lists of these parameters are allowed, default values, boolean-flags (`--foo/--no-foo`), counts
- **Simple**: Pure python, no dependencies
- **Documentation**: Function's docstring creates `--help` documentation. Support for `Sphynx`, `GoogleDoc`, `NumpyDoc`, `EpyText`


## Example
Check out the [list of examples][3] to see the package in action


A quick example (just to get you excited):
```python
import clargs


def count(
    singular: str,
    plural: str,
    maxitems: int = 10,
    *,
    shout: bool = False,
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
```

```console
> python main.py --help
usage: main.py [-h] [--shout [SHOUT]] singular plural [maxitems]

Counts from 1 to given number (default = 10)

positional arguments:
  singular              The singular form of the thing to count
  plural                The plural form of the thing to count
  maxitems              The number to count to

options:
  -h, --help            show this help message and exit
  --shout [SHOUT], -s [SHOUT]
                        If True, will convert all expressions to capitals> python main.py bottle bottles
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

In addition to normal types, the `clargs` package defines some special types.

#### `clargs.Flag`

Is an alias for `bool` (should be recognised by static type-checkers).
Creates `--foo/--no-foo` parameter pair to control booleans


#### `clargs.Count`

Is an alias for `int` (should be recognised by static type-checkers).
Counts how often a parameter is present (mostly used in `--verbose --verbose --verbose` parameters)

#### `clargs.ExistingDirectoryPath`

Is an alias for `pathlib.Path` (should be recognised by static type-checkers).
It adds validation to confirm that the path is existing, and is a directory.

#### `clargs.ExistingFilePath`

Is an alias for `pathlib.Path` (should be recognised by static type-checkers).
It adds validation to confirm that the path is existing, and is a file.

### Custom Type

TODO: Describe how to make custom functions.

### Validation

Experimental support for validation is added, see [this example][6].
There is no clean way yet to give a proper custom error message in case of an
exception.

## Subparsers

Using subparsers it's possible to add multiple functions to your cli. See [an example here][4]

## Debug output

`clargs` uses python's `logging` module to log to `DEBUG` level exactly what is being added to `argparse`'s `add_argument()` function.
By making the logger output this to screen, you can debug what's going on.

See [an example here][5]

## Global Settings

You can control settings on how `clargs` works, by using the `clargs.Clargs` class to call your functions.

```
myclargs = clargs.Clargs(clargs.Settings(...))
myclargs.create_parser_and_run(func)
```

You can use the following settings (as keyword arguments to `Settings`)

### `flag_prefix` (default `--`)
If you want another flag prefix (e.g. `++` or `/` for windows-like flags), set this here.
If you provide your own parser (i.e. you don't use `create_parser()` on the `Clargs` object), you need to make sure you set `prefix_chars` correctly on the parser.

### `short_flag_prefix` (default `-`)
Same but for the short flags

### `generate_short_flags` (default `True`)
If true, short flags are generated (so you can use `-f` instead of `--foo`.
Note that the short flag is only generated for the first parameter starting with a certain letter.

### `positional_and_kw_args_become` (default `positional`)
Python functions can have positional-only arguments (anything before `/`), keyword-only arguments (anything after `*`), and arguments that can be used both positionally and as keywords (default).
Positional-only arguments always become positional commandline arguments. Keyword-only arguments always become keyword commandline arguments (flags).
This parameter determines what to do with arguments that can be both positional and keyword.

- `positional` those arguments are rendered as positional commandline arguments
- `flag` those arguments are rendered as keyword commandline arguments (flags)
- `flag_if_default` those arguments are rendered as flags if they have a default value, else as positional commandline arguments.

### `replace_underscore_with_dash` (default `True`)
If false, underscores are not replaced with dashes for the commandline arguments.
In the default behaviour, a function parameter `foo_bar` will become a flag `--foo-bar`. If this parameter is false, it becomes `--foo_bar`.

This only affects keyword parameters (flags), and subparser commands (so if a subparser is created for the function `count_down`, then the commandline command will be `count-down`.

## Compare to other solutions

There are many other solutions to create command line interfaces from functions.
I don't think it makes sense to create a comparison list of features now, only to have it be not up to date anymore tomorrow.

The reasons that I developed `clargs` is because I could not find any solution that made me happy (based on the features and properties I describe above).


[2]: https://peps.python.org/pep-0484/
[3]: https://github.com/reinhrst/clargs/tree/main/examples/
[4]: https://github.com/reinhrst/clargs/tree/main/examples/4_parse_groups.py
[5]: https://github.com/reinhrst/clargs/tree/main/examples/5_logging.py
[6]: https://github.com/reinhrst/clargs/tree/main/examples/6_validation.py
