from _canvas import *
import _canvas

def _draw_text(text, x, y, font_name='Helvetica', font_size=16.0):
	if isinstance(text, unicode):
		text = text.encode('utf8')
	if isinstance(font_name, unicode):
		font_name = font_name.encode('utf8')
	_canvas._draw_text(text, x, y, font_name, font_size)

def draw_text(txt, x, y, font_name='Helvetica', font_size=16.0):
	# workaround for a bug in _canvas.draw_text()...
  save_gstate()
  translate(float(x), float(y))
  scale(font_size/16.0, font_size/16.0)
  _draw_text(txt, 0.0, 0.0, font_name, 16.0)
  restore_gstate()

def get_text_size(text, font_name='Helvetica', font_size=16.0):
	"""get_text_size(text, font_name='Helvetica', font_size=16.0) -- Get the size of a line of text
		as it is drawn by the draw_text() function as a tuple of (width, height)."""
	if isinstance(text, unicode):
		text = text.encode('utf8')
	if isinstance(font_name, unicode):
		font_name = font_name.encode('utf8')
	return _canvas._get_text_size(text, font_name, font_size)


BLEND_NORMAL			= 0
BLEND_MULTIPLY			= 1
BLEND_SCREEN			= 2
BLEND_OVERLAY			= 3
BLEND_DARKEN			= 4
BLEND_LIGHTEN			= 5
BLEND_COLOR_DODGE		= 6
BLEND_COLOR_BURN		= 7
BLEND_SOFT_LIGHT		= 8
BLEND_HARD_LIGHT		= 9
BLEND_DIFFERENCE		= 10
BLEND_EXCLUSION			= 11
BLEND_HUE				= 12
BLEND_SATURATION		= 13
BLEND_COLOR				= 14
BLEND_LUMINOSITY		= 15
BLEND_CLEAR				= 16
BLEND_COPY				= 17
BLEND_SOURCE_IN			= 18
BLEND_SOURCE_OUT		= 19
BLEND_SOURCE_ATOP		= 20
BLEND_DESTINATION_OVER	= 21
BLEND_DESTINATION_ATOP	= 22
BLEND_XOR				= 23
BLEND_PLUS_DARKER		= 24
BLEND_PLUS_LIGHTER		= 25
