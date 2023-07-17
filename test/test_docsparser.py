import textwrap
from test_simple import Base
from clargs.docsparser import get_parameter_info_from_docstring, Param


class DocParserBase(Base):
    def assertParse(self, docstring, result):
        paraminfo = get_parameter_info_from_docstring(docstring)
        print(docstring)
        print(paraminfo)
        self.assertEqual(paraminfo, result)


class TestSphynxParser(DocParserBase):
    def test_simple(self):
        docstring = textwrap.dedent(
            """\
            :param foo: My foo
            :param bar: My bar
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo"),
                Param(name="bar", description="My bar"),
            ],
        )

    def test_multiline(self):
        docstring = textwrap.dedent(
            """\
            :param foo: My foo
                is larger
                than your foo
                by a loooooot!
            :param bar: My bar
        """
        )

        self.assertParse(
            docstring,
            [
                Param(
                    name="foo",
                    description="My foo is larger than your foo by a loooooot!",
                ),
                Param(name="bar", description="My bar"),
            ],
        )

    def test_multiline_last(self):
        docstring = textwrap.dedent(
            """\
            :param bar: My bar
            :param foo: My foo
                is larger
                than your foo
                by a loooooot!
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="bar", description="My bar"),
                Param(
                    name="foo",
                    description="My foo is larger than your foo by a loooooot!",
                ),
            ],
        )

    def test_multiline_empty_line(self):
        docstring = textwrap.dedent(
            """\
            :param foo: My foo
                is larger

                than your foo
                by a loooooot!
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo is larger"),
            ],
        )

    def test_space_around_colon(self):
        docstring = textwrap.dedent(
            """\
            :param foo : My foo
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo"),
            ],
        )

    def test_typeinfo(self):
        docstring = textwrap.dedent(
            """\
            :param foo(int): My foo
            :param bar(any crarzy combination [here and there])   :    My bar
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", typeinfo="int", description="My foo"),
                Param(
                    name="bar",
                    typeinfo="any crarzy combination [here and there]",
                    description="My bar",
                ),
            ],
        )


class TestEpytextParser(DocParserBase):
    """Not implemented since EpyText is the same as Sphynx, just with @"""

    pass


class TestGoogleDocParser(DocParserBase):
    def test_simple(self):
        docstring = textwrap.dedent(
            """\
            Args:
                foo: My foo
                bar: My bar
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo"),
                Param(name="bar", description="My bar"),
            ],
        )

    def test_more_stuff(self):
        docstring = textwrap.dedent(
            """\
            Bla Bla Bla
            Args:
                foo: My foo
                bar: My bar
            And more shit here
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo"),
                Param(name="bar", description="My bar"),
            ],
        )

    def test_multiline(self):
        docstring = textwrap.dedent(
            """\
            Args:
                foo: My foo
                 is long
                bar: My bar
                 is longER
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo is long"),
                Param(name="bar", description="My bar is longER"),
            ],
        )


class TestNumpyDocParser(DocParserBase):
    def test_simple(self):
        docstring = textwrap.dedent(
            """\
            Parameters
            ----------
            foo:
                My foo
            bar:
                My bar
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo"),
                Param(name="bar", description="My bar"),
            ],
        )

    def test_more_stuff(self):
        docstring = textwrap.dedent(
            """\
            Bla Bla Bla
            Parameters
            ----------
            foo:
                My foo
            bar:
                My bar
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo"),
                Param(name="bar", description="My bar"),
            ],
        )

    def test_multiline(self):
        docstring = textwrap.dedent(
            """\
            Parameters
            ----------
            foo:
                My foo
                is long
            bar:
                My bar
                is longER
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", description="My foo is long"),
                Param(name="bar", description="My bar is longER"),
            ],
        )

    def test_typeinfo(self):
        docstring = textwrap.dedent(
            """\
            Parameters
            ----------
            foo: int
                My foo
            bar: some weird type
                My bar
        """
        )

        self.assertParse(
            docstring,
            [
                Param(name="foo", typeinfo="int", description="My foo"),
                Param(name="bar", typeinfo="some weird type", description="My bar"),
            ],
        )
