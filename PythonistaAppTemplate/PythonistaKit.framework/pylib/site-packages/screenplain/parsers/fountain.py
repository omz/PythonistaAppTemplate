# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import itertools
from itertools import takewhile
import re

from screenplain.types import (
    Slug, Action, Dialog, DualDialog, Transition, Section, PageBreak,
    Screenplay
)
from screenplain.richstring import parse_emphasis, plain

slug_regexes = (
    re.compile(r'^(INT|EXT|EST)[ .]'),
    re.compile(r'^(INT\.?/EXT\.?)[ .]'),
    re.compile(r'^I/E[ .]'),
)

boneyard_re = re.compile(r'/\*.*?\*/', flags=re.DOTALL)

TWOSPACE = ' ' * 2

linebreak_re = re.compile('\r\n|\n|\r')

title_page_key_re = re.compile(r'([^:]+):\s*(.*)')
title_page_value_re = re.compile(r'(?:\s{3,}|\t)(.+)')

centered_re = re.compile(r'\s*>\s*(.*?)\s*<\s*$')
dual_dialog_re = re.compile(r'^(.+?)(\s*\^)$')
slug_re = re.compile(r'(?:(\.)(?=[^.])\s*)?(\S.*?)\s*$')
scene_number_re = re.compile(r'(.*?)\s*(?:#([\w\-.]+)#)\s*$')
section_re = re.compile(r'^(#{1,6})\s*([^#].*)$')
transition_re = re.compile(r'(>?)\s*(.+?)(TO:)?$')
page_break_re = re.compile(r'^={3,}$')


def _sequence_to_rich(lines):
    """Converts a sequence of strings into a list of RichString."""
    return [parse_emphasis(line) for line in lines]


def _string_to_rich(line):
    """Converts a single string into a RichString.
    """
    return parse_emphasis(line)


class InputParagraph(object):
    def __init__(self, lines):
        self.lines = lines

    def update_list(self, previous_paragraphs):
        """Inserts this paragraph into a list.
        Modifies the `previous_paragraphs` list.
        """
        (
            self.append_page_break(previous_paragraphs) or
            self.append_synopsis(previous_paragraphs) or
            self.append_sections_and_synopsises(previous_paragraphs) or
            self.append_slug(previous_paragraphs) or
            self.append_centered_action(previous_paragraphs) or
            self.append_dialog(previous_paragraphs) or
            self.append_transition(previous_paragraphs) or
            self.append_action(previous_paragraphs)
        )

    def append_slug(self, paragraphs):
        if len(self.lines) != 1:
            return False

        match = slug_re.match(self.lines[0])
        if not match:
            return False

        period, text = match.groups()
        text = text.upper()
        if not period and not any(regex.match(text) for regex in slug_regexes):
            return False

        match = scene_number_re.match(text)
        if match:
            text, scene_number = match.groups()
            paragraphs.append(Slug(_string_to_rich(text), plain(scene_number)))
        else:
            paragraphs.append(Slug(_string_to_rich(text)))
        return True

    def append_sections_and_synopsises(self, paragraphs):

        new_paragraphs = []

        for line in self.lines:
            match = section_re.match(line)
            if match:
                hashes, text = match.groups()
                section = Section(_string_to_rich(text), len(hashes))
                new_paragraphs.append(section)
            elif (
                line.startswith('=') and
                new_paragraphs and
                hasattr(new_paragraphs[-1], 'set_synopsis')
            ):
                new_paragraphs[-1].set_synopsis(line[1:].lstrip())
            else:
                return False

        paragraphs += new_paragraphs
        return True

    def append_centered_action(self, paragraphs):
        if not all(centered_re.match(line) for line in self.lines):
            return False
        paragraphs.append(Action(_sequence_to_rich(
            centered_re.match(line).group(1) for line in self.lines
        ), centered=True))
        return True

    def _create_dialog(self, character):
        return Dialog(
            parse_emphasis(character.strip()),
            _sequence_to_rich(line.strip() for line in self.lines[1:])
        )

    def append_dialog(self, paragraphs):
        if len(self.lines) < 2:
            return False

        character = self.lines[0]
        if not character.isupper() or character.endswith(TWOSPACE):
            return False

        if paragraphs and isinstance(paragraphs[-1], Dialog):
            dual_match = dual_dialog_re.match(character)
            if dual_match:
                previous = paragraphs.pop()
                dialog = self._create_dialog(dual_match.group(1))
                paragraphs.append(DualDialog(previous, dialog))
                return True

        paragraphs.append(self._create_dialog(character))
        return True

    def append_transition(self, paragraphs):
        if len(self.lines) != 1:
            return False

        match = transition_re.match(self.lines[0])
        if not match:
            return False
        greater_than, text, to_colon = match.groups()

        if greater_than:
            paragraphs.append(
                Transition(_string_to_rich(text.upper() + (to_colon or '')))
            )
            return True

        if text.isupper() and to_colon:
            paragraphs.append(
                Transition(_string_to_rich(text + to_colon))
            )
            return True

        return False

    def append_action(self, paragraphs):
        paragraphs.append(
            Action(_sequence_to_rich(line.rstrip() for line in self.lines))
        )
        return True

    def append_synopsis(self, paragraphs):
        if (
            len(self.lines) == 1 and
            self.lines[0].startswith('=') and
            paragraphs and
            hasattr(paragraphs[-1], 'set_synopsis')
        ):
            paragraphs[-1].set_synopsis(self.lines[0][1:].lstrip())
            return True
        else:
            return False

    def append_page_break(self, paragraphs):
        if len(self.lines) == 1 and page_break_re.match(self.lines[0]):
            paragraphs.append(PageBreak())
            return True
        else:
            return False


def _preprocess_line(raw_line):
    r"""Replaces tabs with spaces and removes trailing end of line markers.

    >>> _preprocess_line('foo \r\n\n')
    'foo '

    """
    return raw_line.expandtabs(4).rstrip('\r\n')


def _is_blank(line):
    return line == ''


def parse(stream):
    """Parses Fountain source.

    Returns a Screenplay object.

    """
    content = stream.read()
    content = boneyard_re.sub('', content)
    lines = linebreak_re.split(content)
    del content
    return parse_lines(lines)


def parse_lines(source):
    """Reads raw text input and generates paragraph objects.

    Returns a Screenplay object.

    """
    source = (_preprocess_line(line) for line in source)

    title_page_lines = list(takewhile(lambda line: line != '', source))
    title_page = parse_title_page(title_page_lines)

    if title_page:
        # The first lines were a title page.
        # Parse the rest of the source as screenplay body.
        return Screenplay(title_page, parse_body(source))
    else:
        # The first lines were not a title page.
        # Parse them as part of the screenplay body.
        return Screenplay(
            {},
            parse_body(itertools.chain(title_page_lines, [''], source))
        )


def parse_body(source):
    """Reads lines of the main screenplay and generates paragraph objects."""

    paragraphs = []
    for blank, input_lines in itertools.groupby(source, _is_blank):
        if not blank:
            paragraph = InputParagraph(list(input_lines))
            paragraph.update_list(paragraphs)

    return paragraphs


def parse_title_page(lines):
    """Parse the title page.

    Spec: http://fountain.io/syntax#section-titlepage
    Returns None if the document does not have a title page section,
    otherwise a dictionary with the data.
    """
    result = {}

    it = iter(lines)
    try:
        line = it.next()
        while True:
            key_match = title_page_key_re.match(line)
            if not key_match:
                return None
            key, value = key_match.groups()
            if value:
                # Single line key/value
                result.setdefault(key, []).append(value)
                line = it.next()
            else:
                for line in it:
                    value_match = title_page_value_re.match(line)
                    if not value_match:
                        break
                    result.setdefault(key, []).append(value_match.group(1))
                else:
                    # Last line has been processed
                    break
    except StopIteration:
        pass
    return result
