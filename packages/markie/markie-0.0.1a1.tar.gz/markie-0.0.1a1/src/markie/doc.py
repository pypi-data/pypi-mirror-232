from collections.abc import Iterator, Mapping, Sequence
from typing import Any, Self

import mdformat_footnote
import mdformat_frontmatter
import mdformat_tables
import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdformat.renderer import MDRenderer
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

from markie.rules import render_rules
from markie.rules.parsing_rules import wikilink_plugin

MD = (
    MarkdownIt('commonmark', {'breaks': True, 'html': True})
    .use(wikilink_plugin)
    .use(front_matter_plugin)
    .use(footnote_plugin)
    .enable('table')
)

RENDERER = MDRenderer()
OPTIONS = {
    "parser_extension": [
        render_rules,
        mdformat_tables,
        mdformat_footnote,
        mdformat_frontmatter,
    ],
}

HEADING_LEVELS = {
    "h1": 1,
    "h2": 2,
    "h3": 3,
    "h4": 4,
    "h5": 5,
    "h6": 6,
}


def parse_src(src: str) -> tuple[Mapping[str, Any], list[Token]]:
    tokens = MD.parse(src)
    return parse_tokens(tokens)


def parse_tokens(tokens: Sequence[Token]):
    if tokens[0].type == "front_matter":
        frontmatter, *tokens = tokens
        frontmatter = yaml.safe_load(frontmatter.content)
    else:
        frontmatter = {}
    return frontmatter, tokens


class Doc:
    def __init__(self, metadata, content):
        self.metadata = metadata
        self._content: list[Token] = list(content)

    @classmethod
    def from_md(cls, src: str) -> Self:
        """
        Parses the given markdown src string and returns a new Doc.

        :param src: a string of markdown
        """
        frontmatter, tokens = parse_src(src)
        return cls(frontmatter, tokens)

    @classmethod
    def from_tokens(cls, src: Sequence[Token]) -> Self:
        """
        Creates a new Doc from a sequence of markdown-it tokens

        :param src: a sequence of markdown-it tokens
        """
        frontmatter, tokens = parse_tokens(src)
        return cls(frontmatter, tokens)

    def prepend(self, src: str):
        """
        Adds the given content to the start of this Markdown doc. Ignores any
        metadata in the given src string.
        """
        metadata, tokens = parse_src(src)
        self._content = [*tokens, *self._content]

    def append(self, src: str):
        """
        Adds the given content to the end of this Markdown doc. Ignores any
        metadata in the given src string.
        """
        _, tokens = parse_src(src)
        self._content.extend(tokens)

    def append_to_section(self, src: str, title: str, level: str):
        """
        Finds the first section with the given title and level and adds the
        given content to the end of that section

        :param src: the markdown string to add
        :param title: the tile of the section to append to
        :param level: the level of the heading to find
        """
        _, idx = self._section(title, level)
        _, tokens = parse_src(src)
        self._content[idx:idx] = tokens

    def prepend_to_section(self, src: str, title: str, level: str):
        """
        Finds the first section with the given title and level and adds the
        given content to the start of that section

        :param src: the markdown string to add
        :param title: the tile of the section to prepend to
        :param level: the level of the heading to find
        """
        idx, _ = self._section(title, level)
        _, tokens = parse_src(src)
        self._content[idx:idx] = tokens

    def replace_section(self, src: str, title: str, level: str):
        """
        Finds the first section with the given title and level and replaces that
        section's content with the given markdown.
        (The section heading is preserved)

        :param src: the markdown string
        :param title: the tile of the section to replace
        :param level: the level of the heading to find
        """
        s, e = self._section(title, level)
        _, tokens = parse_src(src)
        self._content[s:e] = tokens

    def _section(self, title: str, level: str) -> tuple[int, int]:
        """
        Returns the start and end indices of the given section content

        :param title: the title of the section to find
        :param level: the section level
        """
        it = self._tokens_of_type("heading_open")
        start = next(
            i for i, t in it
            if t.tag == level and self._content[i + 1].content == title
        )
        end, _ = next(it, (len(self._content), None))
        return start + 3, end

    def _tokens_of_type(
          self, *ttypes: str, start: int = 0
    ) -> Iterator[tuple[int, Token]]:
        """
        Iterates over tokens of the given type(s)

        :param ttypes: the types of tokens
        :param start: the index to start searching from
        :returns: an iterator that iterates over the indices and tokens that
            match the given criteria
        """
        for i in range(start, len(self._content)):
            token = self._content[i]
            if token.type in ttypes:
                yield i, token

    def render(self) -> str:
        """Renders this doc as markdown"""
        if self.metadata:
            frontmatter = Token(
                type='front_matter',
                tag='',
                nesting=0,
                content=yaml.safe_dump(self.metadata, sort_keys=False),
                markup='---',
                block=True,
                hidden=True
            )
            tokens = [frontmatter, *self._content]
        else:
            tokens = self._content
        return RENDERER.render(tokens, OPTIONS, {})

    def __add__(self, other: "Doc") -> "Doc":
        """
        Combines this doc with another – only includes metadata from this doc
        and not other
        """
        return Doc(self.metadata, self._content + other._content)

    def __iadd__(self, other: "Doc"):
        """
        Appends the content from other to this – ignores metadata from other.
        """
        self._content += other._content
        return self
