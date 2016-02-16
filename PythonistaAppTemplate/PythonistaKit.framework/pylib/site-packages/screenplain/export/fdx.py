# Copyright (c) 2011 Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

from xml.sax.saxutils import escape

from screenplain.types import *
from screenplain.richstring import RichString
from screenplain.richstring import Bold, Italic, Underline


style_names = {
    Bold: 'Bold',
    Italic: 'Italic',
    Underline: 'Underline',
}


def _write_text_element(out, styles, text):
    style_value = '+'.join(str(s) for s in styles)
    if style_value == '':
        out.write('      <Text>%s</Text>\n' % (escape(text)))
    else:
        out.write(
            '      <Text Style="%s">%s</Text>\n' %
            (style_value, escape(text))
        )


def write_text(out, rich, trailing_linebreak):
    """Writes <Text Style="..."> elements."""
    for seg_no, segment in enumerate(rich.segments):
        fdx_styles = [style_names[n] for n in segment.get_ordered_styles()]
        if trailing_linebreak and seg_no == len(rich.segments) - 1:
            _write_text_element(out, fdx_styles, segment.text + '\n')
        else:
            _write_text_element(out, fdx_styles, segment.text)


def write_paragraph(out, para_type, lines, centered=False):
    if centered:
        out.write('    <Paragraph Alignment="Center" Type="%s">\n' % para_type)
    else:
        out.write('    <Paragraph Type="%s">\n' % para_type)

    last_line_no = len(lines) - 1
    for line_no, line in enumerate(lines):
        write_text(out, line, line_no != last_line_no)
    out.write('    </Paragraph>\n')


def write_dialog(out, dialog):
    write_paragraph(out, 'Character', [dialog.character])
    for parenthetical, line in dialog.blocks:
        if parenthetical:
            write_paragraph(out, 'Parenthetical', [line])
        else:
            write_paragraph(out, 'Dialogue', [line])


def write_dual_dialog(out, dual):
    out.write(
        '    <Paragraph>\n'
        '      <DualDialogue>\n'
    )
    write_dialog(out, dual.left)
    write_dialog(out, dual.right)
    out.write(
        '      </DualDialogue>\n'
        '    </Paragraph>\n'
    )


def to_fdx(screenplay, out):

    out.write(
        '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'
        '<FinalDraft DocumentType="Script" Template="No" Version="1">\n'
        '\n'
        '  <Content>\n'
    )

    for para in screenplay:
        if isinstance(para, Dialog):
            write_dialog(out, para)
        elif isinstance(para, DualDialog):
            write_dual_dialog(out, para)
        elif isinstance(para, Action):
            write_paragraph(out, 'Action', para.lines, centered=para.centered)
        elif isinstance(para, Slug):
            write_paragraph(out, 'Scene Heading', para.lines)
        elif isinstance(para, Transition):
            write_paragraph(out, 'Transition', para.lines)
        else:
            # Ignore unknown types
            pass

    out.write(
        '  </Content>\n'
        '</FinalDraft>\n'
    )
