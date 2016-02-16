# Copyright (c) 2014 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import sys

try:
    import reportlab
except ImportError:
    sys.stderr.write('ERROR: ReportLab is required for PDF output\n')
    raise
del reportlab

from reportlab.lib import pagesizes
from reportlab.platypus import (
    BaseDocTemplate,
    Paragraph,
    Frame,
    PageTemplate,
    Spacer,
)
from reportlab import platypus
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from screenplain.types import (
    Action, Dialog, DualDialog, Transition, Slug
)
from screenplain import types

lines_per_page = 55
characters_per_line = 61
frame_height = 12 * lines_per_page
frame_width = characters_per_line * 72 / 10.0  # Courier pitch is 10 chars/inch
page_width, page_height = pagesizes.letter
left_margin = 1.5 * inch
right_margin = page_width - left_margin - frame_width
top_margin = 1 * inch
bottom_margin = page_height - top_margin - frame_height

character_width = 1.0 / 10 * inch

default_style = ParagraphStyle(
    'default',
    fontName='Courier',
    fontSize=12,
    leading=12,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
)
centered_style = ParagraphStyle(
    'default-centered', default_style,
    alignment=TA_CENTER,
)

# Screenplay styles
character_style = ParagraphStyle(
    'character', default_style,
    spaceBefore=12,
    leftIndent=19 * character_width,
    keepWithNext=1,
)
dialog_style = ParagraphStyle(
    'dialog', default_style,
    leftIndent=9 * character_width,
    rightIndent=frame_width - (45 * character_width),
)
parenthentical_style = ParagraphStyle(
    'parenthentical', default_style,
    leftIndent=13 * character_width,
    keepWithNext=1,
)
action_style = ParagraphStyle(
    'action', default_style,
    spaceBefore=12,
)
centered_action_style = ParagraphStyle(
    'centered-action', action_style,
    alignment=TA_CENTER,
)
slug_style = ParagraphStyle(
    'slug', default_style,
    spaceBefore=12,
    spaceAfter=12,
    keepWithNext=1,
)
transition_style = ParagraphStyle(
    'transition', default_style,
    spaceBefore=12,
    spaceAfter=12,
)

# Title page styles
title_style = ParagraphStyle(
    'title', default_style,
    fontSize=24, leading=36,
    alignment=TA_CENTER,
)
contact_style = ParagraphStyle(
    'contact', default_style,
    leftIndent=3.9 * inch,
    rightIndent=0,
)


class DocTemplate(BaseDocTemplate):
    def __init__(self, *args, **kwargs):
        self.has_title_page = kwargs.pop('has_title_page', False)
        frame = Frame(
            left_margin, bottom_margin, frame_width, frame_height,
            id='normal',
            leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0
        )
        pageTemplates = [
            PageTemplate(id='standard', frames=[frame])
        ]
        BaseDocTemplate.__init__(
            self, pageTemplates=pageTemplates, *args, **kwargs
        )

    def handle_pageBegin(self):
        self.canv.setFont('Courier', 12, leading=12)
        if self.has_title_page:
            page = self.page  # self.page is 0 on first page
        else:
            page = self.page + 1
        if page >= 2:
            self.canv.drawRightString(
                left_margin + frame_width,
                page_height - 42,
                '%s.' % page
            )
        self._handle_pageBegin()


def add_paragraph(story, para, style):
    for line in para.lines:
        story.append(Paragraph(line.to_html(), style))


def add_dialog(story, dialog):
    story.append(Paragraph(dialog.character.to_html(), character_style))
    for parenthetical, line in dialog.blocks:
        if parenthetical:
            story.append(Paragraph(line.to_html(), parenthentical_style))
        else:
            story.append(Paragraph(line.to_html(), dialog_style))


def add_dual_dialog(story, dual):
    # TODO: format dual dialog
    add_dialog(story, dual.left)
    add_dialog(story, dual.right)


def get_title_page_story(screenplay):
    """Get Platypus flowables for the title page

    """
    # From Fountain spec:
    # The recommendation is that Title, Credit, Author (or Authors, either
    # is a valid key syntax), and Source will be centered on the page in
    # formatted output. Contact and Draft date would be placed at the lower
    # left.

    def add_lines(story, attribute, style, space_before=0):
        lines = screenplay.get_rich_attribute(attribute)
        if not lines:
            return 0

        if space_before:
            story.append(Spacer(frame_width, space_before))

        total_height = 0
        for line in lines:
            html = line.to_html()
            para = Paragraph(html, style)
            width, height = para.wrap(frame_width, frame_height)
            story.append(para)
            total_height += height
        return space_before + total_height

    title_story = []
    title_height = sum((
        add_lines(title_story, 'Title', title_style),
        add_lines(title_story, 'Credit', centered_style, space_before=12),
        add_lines(title_story, 'Author', centered_style),
        add_lines(title_story, 'Authors', centered_style),
        add_lines(title_story, 'Source', centered_style),
    ))

    lower_story = []
    lower_height = sum((
        add_lines(lower_story, 'Draft date', default_style),
        add_lines(lower_story, 'Contact', contact_style, space_before=12),
        add_lines(lower_story, 'Copyright', centered_style, space_before=12),
    ))

    if not title_story and not lower_story:
        return []

    story = []
    top_space = min(
        frame_height / 3.0,
        frame_height - lower_height - title_height
    )
    if top_space > 0:
        story.append(Spacer(frame_width, top_space))
    story += title_story
    # The minus 6 adds some room for rounding errors and whatnot
    middle_space = frame_height - top_space - title_height - lower_height - 6
    if middle_space > 0:
        story.append(Spacer(frame_width, middle_space))
    story += lower_story

    story.append(platypus.PageBreak())
    return story


def to_pdf(screenplay, output_filename, template_constructor=DocTemplate):
    story = get_title_page_story(screenplay)
    has_title_page = bool(story)

    for para in screenplay:
        if isinstance(para, Dialog):
            add_dialog(story, para)
        elif isinstance(para, DualDialog):
            add_dual_dialog(story, para)
        elif isinstance(para, Action):
            add_paragraph(
                story, para,
                centered_action_style if para.centered else action_style
            )
        elif isinstance(para, Slug):
            add_paragraph(story, para, slug_style)
        elif isinstance(para, Transition):
            add_paragraph(story, para, transition_style)
        elif isinstance(para, types.PageBreak):
            story.append(platypus.PageBreak())
        else:
            # Ignore unknown types
            pass

    doc = template_constructor(
        output_filename,
        pagesize=(page_width, page_height),
        has_title_page=has_title_page
    )
    doc.build(story)
