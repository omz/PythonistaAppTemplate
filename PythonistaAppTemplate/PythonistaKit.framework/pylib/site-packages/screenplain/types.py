# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from screenplain.richstring import parse_emphasis


class Screenplay(object):
    def __init__(self, title_page=None, paragraphs=None):
        """
        Create a Screenplay object.

        `title_page` is a dictionary mapping string keys to strings.
        `paragraphs` is a sequence of paragraph objects.
        """

        # Key/value pairs for title page
        if title_page is None:
            self.title_page = {}
        else:
            self.title_page = title_page

        # The paragraphs of the actual script
        if paragraphs is None:
            self.paragraphs = []
        else:
            self.paragraphs = paragraphs

    def get_rich_attribute(self, name, default=[]):
        """Get an attribute from the title page parsed into a RichString.
        Returns a list of RichString objects.

        E.g. `screenplay.get_rich_attribute('Title')`

        """
        if name in self.title_page:
            return [parse_emphasis(line) for line in self.title_page[name]]
        else:
            return default

    def append(self, paragraph):
        """Append a paragraph to this screenplay."""
        self.paragraphs.append(paragraph)

    def __iter__(self):
        """Get an iterator over the paragraphs of this screenplay."""
        return iter(self.paragraphs)


class Slug(object):

    def __init__(self, line, scene_number=None):
        """Creates a scene heading (slug).
        The line parameter is a RichString with the slugline.
        The scene_number parameter is an optional RichString.

        """
        self.line = line
        self.scene_number = scene_number
        self.synopsis = None

    @property
    def lines(self):
        return [self.line]

    def set_synopsis(self, text):
        self.synopsis = text


class Section(object):
    """A section heading."""

    def __init__(self, text, level, synopsis=None):
        self.text = text
        self.level = level
        self.synopsis = synopsis

    def set_synopsis(self, text):
        self.synopsis = text

    def __repr__(self):
        return 'Section(%r, %r, %r)' % (self.text, self.level, self.synopsis)

    def __eq__(self, other):
        return (
            self.text == other.text and
            self.level == other.level and
            self.synopsis == other.synopsis
        )


class Dialog(object):
    def __init__(self, character, lines=None):
        self.character = character
        self.blocks = []  # list of tuples of (is_parenthetical, text)
        if lines:
            self._parse(lines)

    def _parse(self, lines):
        inside_parenthesis = False
        for line in lines:
            if line.startswith('('):
                inside_parenthesis = True
            self.blocks.append((inside_parenthesis, line))
            if line.endswith(')'):
                inside_parenthesis = False

    def add_line(self, line):
        parenthetical = line.startswith('(')
        self.blocks.append((parenthetical, line))


class DualDialog(object):
    def __init__(self, left_dialog, right_dialog):
        self.left = left_dialog
        self.right = right_dialog


class Action(object):
    def __init__(self, lines, centered=False):
        self.lines = lines
        self.centered = centered


class Transition(object):
    def __init__(self, line):
        self.line = line

    @property
    def lines(self):
        return [self.line]


class PageBreak(object):
    pass
