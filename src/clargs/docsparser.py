import re
import textwrap
import inspect
import dataclasses
import typing as t

"""
Parses function documentation to get to the parameters.

It supports the following formats:

Sphynx:
```
:param param1: this is a param
:param param2: this is a very
 long param description


```



Epytext: https://epydoc.sourceforge.net/epytextintro.html

```
@param param1: this is a param
@param param2: this is a very
 long param description

```


Googledoc: https://google.github.io/styleguide/pyguide.html#doc-function-args

```
Args:
    paramname: bla bla
      bla bla
    param2:
        bla bla bla
```

Or

```
Args:
    paramname(int): bla bla
      bla bla
    param2(bool):
        bla bla bla
```


Numpydoc: http://daouzli.com/blog/docstring.html#numpydoc

```
Parameters
----------
param1 : int
    Description of parameter `param1`.
param2 : {'value1', 'value2'}
    Description of a parameter with two possible values.
paramX, paramY : array_like
    Parameter array.
param3 : list of str, optional
    Description of parameter `param3`.
    Its default value is ["value"].
```

"""


@dataclasses.dataclass(kw_only=True)
class Param:
    name: str
    typeinfo: t.Optional[str] = None
    description: str

    def __post_init__(self):
        self.description = re.sub(r"\n\s*", " ", self.description)


@dataclasses.dataclass(frozen=True, kw_only=True)
class FormatParser:
    section_extractor_re: t.Optional[t.Pattern] = None
    param_extractor_re: t.Pattern

    def extract_parameters(self, docstring: str) -> t.Sequence[Param]:
        if self.section_extractor_re:
            section = "\n".join(
                [
                    textwrap.dedent(match.group("section"))
                    for match in self.section_extractor_re.finditer(docstring)
                ]
            )
        else:
            section = docstring

        return [
            Param(**match.groupdict())
            for match in self.param_extractor_re.finditer(section)
        ]


def _get_keyword_start_parser_regex(keyword: str) -> t.Pattern:
    return re.compile(
        r"^"
        "" + re.escape(keyword) + r"\s*"
        r"(?P<name>\w+)\s*"  # :param NAME at start of line
        r"(?:\((?P<typeinfo>[^\)]*)\))?\s*"  # optional (TYPE)
        r":\s*"  # colon and whitespace
        r"(?P<description>.*?$)"  # description multi lines
        r"(?=\s*(?:\Z|^[^ \t]|^$))",  # ends at EOF or \n\n or no indent
        re.MULTILINE | re.DOTALL,
    )


def _get_numpy_param_parser_regex() -> t.Pattern:
    return re.compile(
        r"^"
        r"(?P<name>\w+)\s*"  # :param NAME at start of line
        r":[ \t]*"  # colon and whitespace
        r"(?:(?P<typeinfo>[^\n]+))?"  # optional (TYPE)
        r"\n[ \t]*"  # newline
        r"(?P<description>.*?$)"  # description multi lines
        r"(?=\s*(?:\Z|^[^ \t]|^$))",  # ends at EOF or \n\n or no indent
        re.MULTILINE | re.DOTALL,
    )


def _get_section_paragraph_regex(
    section_start_re_str: str, *, no_indent_ends_section: bool
) -> t.Pattern:
    return re.compile(
        r"^" + section_start_re_str + r"(?P<section>.*?)"
        r"(?=\s*(?:\Z|^$" + (r"|^[^ \t]" if no_indent_ends_section else "") + "))",
        re.MULTILINE | re.DOTALL,
    )


FORMAT_PARSERS = {
    "sphynx": FormatParser(
        param_extractor_re=_get_keyword_start_parser_regex(":param ")
    ),
    "epytext": FormatParser(
        param_extractor_re=_get_keyword_start_parser_regex("@param ")
    ),
    "googledoc": FormatParser(
        section_extractor_re=_get_section_paragraph_regex(
            "Args:\n", no_indent_ends_section=True
        ),
        param_extractor_re=_get_keyword_start_parser_regex(""),
    ),
    "numpydoc": FormatParser(
        section_extractor_re=_get_section_paragraph_regex(
            "Parameters:?\n-+\n", no_indent_ends_section=False
        ),
        param_extractor_re=_get_numpy_param_parser_regex(),
    ),
}


def get_parameter_info_from_docstring(docstring: str) -> t.Sequence[Param]:
    results: t.Sequence[Param] = []
    for parser in FORMAT_PARSERS.values():
        parser_results = parser.extract_parameters(docstring)
        if len(parser_results) > len(results):
            results = parser_results
    return results


if __name__ == "__main__":
    docstring = textwrap.dedent(
        """\
        This is some info:

        Args:
            paramname(int): bla bla
              bla bla
            param2(bool):
                bla bla bla

        Parameters
        ----------
        param1 : int
            Description of parameter `param1`.
        param2 : {'value1', 'value2'}
            Description of a parameter with two possible values.
        paramX, paramY : array_like
            Parameter array.
        param3 : list of str, optional
            Description of parameter `param3`.
            Its default value is ["value"].

        :param spynxparam: this is an (important) param
        :param sphynxint(int): this is an (unimportant) very
         long param description
        :param sphynx(str or int):
            this is an description starting on the next line
            and going for two lines
        :param sphynx3(list[str]):
            this is an description starting on the next line
            and going for two lines

            but this is not anymore the description

        @param epytextparam: this is a param
        @param epytextint(int): this is a very
         long param description
         """
    )
    for name, parser in FORMAT_PARSERS.items():
        print(f"{name}: {parser.extract_parameters(docstring)}")
