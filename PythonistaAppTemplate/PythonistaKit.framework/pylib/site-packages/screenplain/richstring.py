# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import re
import cgi

_magic_re = re.compile(u'[\ue700-\ue705]')


class RichString(object):
    """A sequence of segments where each segment can have its own style."""

    def __init__(self, *segments):
        self.segments = segments

    def __repr__(self):
        if not self.segments:
            return "empty_string"
        return ' + '.join(repr(s) for s in self.segments)

    def __unicode__(self):
        return ''.join(unicode(s) for s in self.segments)

    def startswith(self, string):
        """Checks if the first segment in this string starts with a
        specific string.

        """
        if '' == string:
            return True
        if not self.segments:
            return False
        return self.segments[0].text.startswith(string)

    def endswith(self, string):
        """Checks if the last segment in this string ends with a
        specific string.

        """
        if '' == string:
            return True
        if not self.segments:
            return False
        return self.segments[-1].text.endswith(string)

    def to_html(self):
        return ''.join(seg.to_html() for seg in self.segments)

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.segments == other.segments
        )

    def __ne__(self, other):
        return (
            type(self) != type(other) or
            self.segments != other.segments
        )

    def __add__(self, other):
        if hasattr(other, 'segments'):
            return RichString(*(self.segments + other.segments))
        else:
            raise ValueError('Concatenating requires RichString')


class Segment(object):
    """A piece of a rich string. Has a set of styles."""

    def __init__(self, text, styles):
        """
        Creates a segment with a set of styles.
        text is the raw text string, and
        styles is a set of Style subclasses.
        """
        self.styles = set(styles)
        self.text = text

    def __repr__(self):
        return '(%s)(%r)' % (
            '+'.join(
                style.name() for style in self.get_ordered_styles()
            ) or 'plain',
            self.text
        )

    def __unicode__(self):
        return self.text

    def __eq__(self, other):
        return (
            isinstance(other, Segment) and
            self.text == other.text and self.styles == other.styles
        )

    def __ne__(self, other):
        return (
            not isinstance(other, Segment) or
            self.text != other.text or self.styles != other.styles
        )

    def get_ordered_styles(self):
        """Get the styles in this segment in a deterministic order."""
        return [style for style in all_styles if style in self.styles]

    def to_html(self):
        ordered_styles = self.get_ordered_styles()
        return (
            ''.join(style.start_html for style in ordered_styles) +
            cgi.escape(self.text).encode('ascii', 'xmlcharrefreplace') +
            ''.join(style.end_html for style in reversed(ordered_styles))
        )


class Style(object):
    """Abstract base class for styles"""

    start_magic = ''
    end_magic = ''
    start_html = ''
    end_html = ''

    @classmethod
    def name(cls):
        return cls.__name__.lower()


class Italic(Style):

    parse_re = re.compile(
        # one star
        r'\*'
        # anything but a space, then text
        r'([^\s].*?)'
        # finishing with one star
        r'\*'
        # must not be followed by star
        r'(?!\*)'
    )

    start_magic = u'\ue700'
    end_magic = u'\ue701'

    start_html = '<em>'
    end_html = '</em>'


class Bold(Style):

    parse_re = re.compile(
        # two stars
        r'\*\*'
        # must not be followed by space
        r'(?=\S)'
        # inside text
        r'(.+?[*_]*)'
        # finishing with two stars
        r'(?<=\S)\*\*'
    )

    start_magic = u'\ue702'
    end_magic = u'\ue703'

    start_html = '<strong>'
    end_html = '</strong>'


class Underline(Style):

    parse_re = re.compile(
        # underline
        r'_'
        # must not be followed by space
        r'(?=\S)'
        # inside text
        r'([^_]+)'
        # finishing with underline
        r'(?<=\S)_'
    )

    start_magic = u'\ue704'
    end_magic = u'\ue705'

    start_html = '<u>'  # TODO: use an actual html5 tag
    end_html = '</u>'


class _CreateStyledString(object):
    """Function object that creates a RichString object
    with a single segment with a specified style.
    """
    def __init__(self, styles):
        self.styles = set(styles)

    def __call__(self, text):
        return RichString(Segment(text, self.styles))

    def __add__(self, other):
        return _CreateStyledString(self.styles.union(other.styles))

plain = _CreateStyledString(())
bold = _CreateStyledString((Bold,))
italic = _CreateStyledString((Italic,))
underline = _CreateStyledString((Underline,))

empty_string = RichString()

# A special unicode character to use for a literal '*'
literal_star = u'\ue706'

# All styles. Note: order matters! This is the order they are parsed.
all_styles = (Bold, Italic, Underline)


def _unescape(source):
    r"""Converts backslash-escaped stars in a string to the magic
    "literal star" character.

    >>> _unescape(r'\*hello\*')
    u'\ue706hello\ue706'

    """
    return source.replace('\\*', literal_star)


def _demagic_literals(text):
    r"""Converts "literal star" characters to actual stars: "*"

    >>> _demagic_literals(u'\ue706hello\ue706')
    u'*hello*'
    """
    return text.replace(literal_star, '*')


def parse_emphasis(source):
    """Parses emphasis markers like * and ** in a string
    and returns a RichString object.

    >>> parse_emphasis(u'**hello**')
    (bold)(u'hello')
    >>> parse_emphasis(u'plain')
    (plain)(u'plain')
    >>> parse_emphasis(u'**hello** there')
    (bold)(u'hello') + (plain)(u' there')
    """

    # Convert escaped characters to magic characters so they aren't parsed
    # as emphasis.
    source = _unescape(source)

    for style in all_styles:
        source = style.parse_re.sub(
            style.start_magic + r'\1' + style.end_magic, source
        )

    # Convert magic characters back, so they are printable again.
    source = _demagic_literals(source)

    styles = set()
    segments = []
    pos = 0

    def append(pos, end):
        if(pos == end):
            return
        text = source[pos:end]
        segments.append(Segment(text, styles))

    for match in _magic_re.finditer(source):
        end = match.start()
        append(pos, end)
        pos = end + 1
        magic = match.group(0)
        for style in all_styles:
            if magic == style.start_magic:
                styles.add(style)
            elif magic == style.end_magic:
                styles.remove(style)
    append(pos, len(source))

    return RichString(*segments)
