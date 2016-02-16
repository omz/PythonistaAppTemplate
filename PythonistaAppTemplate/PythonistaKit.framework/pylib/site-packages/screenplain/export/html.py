# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from __future__ import with_statement
import sys
import re
import cgi
import os
import os.path

from screenplain.types import *
from screenplain.richstring import plain


class tag(object):
    """Handler for automatically opening and closing a tag.

    E.g.

    >>> import sys
    >>> from __future__ import with_statement
    >>> with tag(sys.stdout, 'div'):
    ...     sys.stdout.write('hello')
    ...
    <div>hello</div>

    Adding classes to the element is possible:

    >>> with tag(sys.stdout, 'div', classes=['action']):
    ...     sys.stdout.write('hello')
    <div class="action">hello</div>

    >>> with tag(sys.stdout, 'div', classes=['action', 'centered']):
    ...     sys.stdout.write('hello')
    <div class="action centered">hello</div>

    """
    def __init__(self, out, tag, classes=None):
        self.out = out
        self.tag = tag
        self.classes = classes

    def __enter__(self):
        if self.classes:
            self.out.write('<%s class="%s">' % (
                self.tag,
                ' '.join(self.classes)
            ))
        else:
            self.out.write('<%s>' % self.tag)

    def __exit__(self, exception_type, value, traceback):
        if not exception_type:
            self.out.write('</%s>' % self.tag)
        return False


def to_html(text):
    html = text.to_html()
    if html == '':
        return '&nbsp;'
    return re.sub('  ', '&nbsp; ', html)


class Formatter(object):
    """Class for converting paragraphs into HTML."""

    def __init__(self, out):
        """Initializes the formatter.

        `out` is a file-like object to write to.
        After initializing, call the convert function to convert
        any number of paragraphs.

        """
        self.out = out
        self._format_functions = {
            Slug: self.format_slug,
            Action: self.format_action,
            Dialog: self.format_dialog,
            DualDialog: self.format_dual,
            Transition: self.format_transition,
            Section: self.format_section,
            PageBreak: self.format_page_break,
        }

    def convert(self, screenplay):
        """Converts a number of paragraphs into HTML and writes
        it to the output stream.
        `screenplay` is a sequence of paragraphs.

        """
        self.page_break_before_next = False
        for para in screenplay:
            format_function = self._format_functions.get(type(para), None)
            if format_function:
                format_function(para)
                self.out.write('\n')

    def format_dialog(self, dialog):
        with self._tag('div', classes=['dialog']):
            self._write_dialog_block(dialog)

    def format_dual(self, dual):
        with self._tag('div', classes=['dual']):
            with self._tag('div', classes=['left']):
                self._write_dialog_block(dual.left)
            with self._tag('div', classes=['right']):
                self._write_dialog_block(dual.right)
            self.out.write('<br />')

    def _write_dialog_block(self, dialog):
        with self._tag('p', classes=['character']):
            self.out.write(to_html(dialog.character))

        for parenthetical, text in dialog.blocks:
            classes = ['parenthetical'] if parenthetical else None
            with self._tag('p', classes=classes):
                self.out.write(to_html(text))

    def format_slug(self, slug):
        num = slug.scene_number
        with self._tag('h6'):
            if num:
                with self._tag('span', classes=['scnuml']):
                    self.out.write(to_html(slug.scene_number))
            self.out.write(to_html(slug.line))
            if num:
                with self._tag('span', classes=['scnumr']):
                    self.out.write(to_html(slug.scene_number))
        if slug.synopsis:
            with self._tag('span', classes=['h6-synopsis']):
                self.out.write(to_html(plain(slug.synopsis)))

    def format_section(self, section):
        with self._tag('h%d' % section.level):
            self.out.write(to_html(section.text))
        if section.synopsis:
            with self._tag('span', classes=['h%d-synopsis' % section.level]):
                self.out.write(to_html(plain(section.synopsis)))

    def format_action(self, para):
        classes = ['action']
        if para.centered:
            classes.append('centered')
        with self._tag('div', classes=classes):
            with self._tag('p'):
                for number, line in enumerate(para.lines):
                    if number != 0:
                        self.out.write('<br/>')
                    self.out.write(to_html(line))

    def format_transition(self, para):
        with self._tag('div', classes=['transition']):
            self.out.write(to_html(para.line))

    def format_page_break(self, para):
        self.page_break_before_next = True

    def _tag(self, tag_name, classes=[]):
        if self.page_break_before_next:
            self.page_break_before_next = False
            classes = set(classes).union(('page-break',))
        return tag(self.out, tag_name, classes)


def _read_file(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as stream:
        return stream.read()


def convert(screenplay, out, bare=False):
    """Convert the screenplay into HTML, written to the file-like object `out`.

    The output will be a complete HTML document unless `bare` is true.

    """
    if bare:
        convert_bare(screenplay, out)
    else:
        convert_full(screenplay, out)


def convert_full(screenplay, out):
    """Convert the screenplay into a complete HTML document,
    written to the file-like object `out`.

    """
    css = _read_file('default.css')
    out.write(
        '<!DOCTYPE html>\n'
        '<html>'
        '<head>'
        '<title>Screenplay</title>'
        '<style type="text/css">'
    )
    out.write(css)
    out.write(
        '</style>'
        '</head>'
        '<body>'
        '<div id="wrapper" class="screenplay">\n'
    )
    convert_bare(screenplay, out)
    out.write(
        '</div>'
        '</body>'
        '</html>\n'
    )


def convert_bare(screenplay, out):
    """Convert the screenplay into HTML, written to the file-like object `out`.
    Does not create a complete HTML document, as it doesn't include
    <html>, <body>, etc.

    """
    formatter = Formatter(out)
    formatter.convert(screenplay)
