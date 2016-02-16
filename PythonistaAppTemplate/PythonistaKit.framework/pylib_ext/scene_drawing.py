from _scene2 import *
import _scene2
from _scene_types import Vector3, Color
import math
from numbers import Number
from io import BytesIO
import ui

def size():
	return ui.get_screen_size()

def image_quad(image_name, x1, y1, x2, y2, x3, y3, x4, y4, from_x1=None, from_y1=None, from_x2=None, from_y2=None, from_x3=None, from_y3=None, from_x4=None, from_y4=None):
	points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
	texture = Texture(image_name)
	w, h = texture.size
	if from_x1 is None:
		from_x1 = 0
		from_y1 = 0
		from_x2 = w
		from_y2 = 0
		from_x3 = 0
		from_y3 = h
		from_x4 = w
		from_y4 = h
	uv_coords = [(x/w, y/h) for x, y in [(from_x1, from_y1), (from_x2, from_y2), (from_x3, from_y3), (from_x4, from_y4)]]
	triangle_strip(points, uv_coords, image_name)
	
def load_pil_image(image):
	b = BytesIO()
	image.save(b, 'PNG')
	return load_image_data(b.getvalue())

def render_text(txt, font_name='Helvetica', font_size=16.0):
	if isinstance(txt, unicode):
		txt = txt.encode('utf8')
	image_name, w, h = _scene2.render_text(txt, font_name, font_size)
	return image_name, Size(w, h)

def text(txt, font_name='Helvetica', font_size=16.0, x=0.0, y=0.0, alignment=5):
	img, size = render_text(txt, font_name, font_size)
	w = size.w
	h = size.h
	#Note: Alignment is in terms of a numeric keypad
	#(5 is vertically and horizontally centered, 1 is bottom left, etc.)
	
	#Vertically centered:
	if alignment == 5:
		image(img, x - w * 0.5, y - h * 0.5, w, h)
	elif alignment == 6:
		image(img, x, y - h * 0.5, w, h)
	elif alignment == 4:
		image(img, x - w, y - h * 0.5, w, h)
	
	#Bottom:
	elif alignment == 8:
		image(img, x - w * 0.5, y, w, h)
	elif alignment == 9:
		image(img, x, y, w, h)
	elif alignment == 7:
		image(img, x - w, y, w, h)
		
	#Top:
	elif alignment == 2:
		image(img, x - w * 0.5, y - h, w, h)
	elif alignment == 3:
		image(img, x, y - h, w, h)
	elif alignment == 1:
		image(img, x - w, y - h, w, h)
	

def curve_sinodial(x):
	y = 0.5 * math.sin(math.pi * x - 0.5 * math.pi) + 0.5
	return y
def curve_linear(x):
	return x
def curve_ease_in(x):
	return x ** 3
def curve_ease_out(x):
	return (x-1)**3 + 1
def curve_ease_in_out(x):
	if x / 0.5 < 1.0:
		x /= 0.5
		return 0.5 * (x ** 3)
	x /= 0.5
	x -= 2
	return 0.5 * (x ** 3 + 2)
def curve_elastic_out(x):
	c = 1.0
	d = 1.0
	b = 0.0
	t = x
	s = 1.70158
	p = 0
	a = c
	if t == 0: return b
	if ((t / d) == 1): return b + c
	if p == 0: p = d * 0.3
	if a < abs(c):
		a = c
		s = p / 4.0
	else:
		s = p / (2 * math.pi) * math.asin(c / a)
	return a * 2 ** (-10*t) * math.sin((t * d - s) * (2 * math.pi)/p) + c + b
def curve_elastic_in(x):
	c = 1.0
	d = 1.0
	b = 0.0
	t = x
	s = 1.70158
	p = 0
	a = c
	if t == 0: return b
	if ((t / d) == 1): return b + c
	if p == 0: p = d * 0.3
	if a < abs(c):
		a = c
		s = p / 4.0
	else:
		s = p / (2 * math.pi) * math.asin(c / a)
	t -= 1
	return -(a*math.pow(2,10*(t)) * math.sin( (t*d-s)*(2*math.pi)/p )) + b
def curve_elastic_in_out(x):
	c = 1.0
	d = 1.0
	b = 0.0
	t = x
	s = 1.70158
	p = 0
	a = c
	if t == 0: return b
	t /= d/2
	if t == 2: return b + c
	if p == 0: p = d * (0.3 * 1.5)
	if a < abs(c):
		a = c
		s = p / 4.0
	else:
		s = p / (2 * math.pi) * math.asin(c / a)
	if t < 1:
		t -= 1
		return -0.5 * (a * math.pow(2, 10 * (t)) * math.sin((t * d - s) * (2 * math.pi) / p)) + b
	t -=1
	return a * math.pow(2, -10 * t) * math.sin((t * d - s) * (2 * math.pi) / p) * 0.5 + c + b
def curve_bounce_out(x):
	c = 1.0
	d = 1.0
	b = 0.0
	t = x
	if (t / d) < (1.0 / 2.75):
		return c * (7.5625*t*t) + b
	elif t < (2.0/2.75):
		t -= (1.5/2.75)
		return c * (7.5625 * t * t + 0.75) + b
	elif t < (2.5 / 2.75):
		t -= (2.25/2.75)
		return c * (7.5625 * t * t + 0.9375) + b
	else:
		t -= (2.625/2.75)
		return c * (7.5625 * t * t + 0.984375) + b
def curve_bounce_in(x):
	return 1.0 - curve_bounce_out(1.0 - x)
def curve_bounce_in_out(x):
	t = x
	d = 1.0
	if t < (d / 2.0):
		return curve_bounce_in(x * 2) * 0.5
	return curve_bounce_out(x * 2 - d) * 0.5 + 0.5

def curve_ease_back_in(x):
	s = 1.70158
	return x * x * ((s+1) * x - s)
def curve_ease_back_out(x):
	s = 1.70158
	t = x - 1
	return (t * t * ((s+1) * t + s) + 1)
def curve_ease_back_in_out(x):
	s = 1.70158
	t = x
	b = 0.0
	c = 1.0
	d = 1.0
	t /= d/2
	if (t < 1):
		s *= 1.525
		return c/2 * (t*t*((s+1)*t - s)) + b;
	t -= 2
	s *= 1.525
	return c/2 * (t*t*((s+1)*t + s) + 2) + b;

class Animation (object):
	def __init__(self):
		self.t = 0.0
		self.repeat = 1
		self._repetitions = 0
		self.autoreverse = False
		self.value = None
		self.from_value = None
		self.to_value = None
		self.duration = 0.5
		self.delay = 0.0
		self.curve = curve_sinodial
		self.completion = None
		self.finished = False
		self.layer = None
		self.attribute = None
	
	def update(self, dt):
		self.t += dt
		progress = 0.0
		if self.t < self.delay: 
			self.value = self.from_value
			return
		else:
			progress = 1.0 if self.duration <= 0 else min(1.0, (self.t - self.delay) / self.duration)
		
		self.value = self.interpolate(progress)
		if isinstance(self.layer, Layer) and self.attribute is not None:
			setattr(self.layer, self.attribute, self.value)
		if progress >= 1.0 and not self.finished:
			self._repetitions += 1
			self.delay = 0.0
			if ((not self.autoreverse and self._repetitions >= self.repeat) or 
				(self.autoreverse and self._repetitions >= self.repeat * 2)):
				self.finished = True
				if isinstance(self.layer, Layer):
					self.layer.remove_animation(self)
				if callable(self.completion):
					self.completion()
			else:
				self.t = 0.0
				if self.autoreverse:
					self.to_value, self.from_value = self.from_value, self.to_value
				else:
					self.value = self.from_value
	
	def interpolate(self, progress):
		p = self.curve(progress)
		from_v = self.from_value
		to_v = self.to_value
		if isinstance(from_v, Number) and isinstance(to_v, Number):
			return from_v + (to_v - from_v) * p
		elif isinstance(self.from_value, Rect) and isinstance(self.to_value, Rect):
			from_x = from_v.x
			from_y = from_v.y
			to_x = to_v.x
			to_y = to_v.y
			from_w = from_v.w
			from_h = from_v.h
			to_w = to_v.w
			to_h = to_v.h
			value = Rect(from_x + (to_x - from_x) * p, from_y + (to_y - from_y) * p, from_w + (to_w - from_w) * p, from_h + (to_h - from_h) * p)
			return value
		elif isinstance(self.from_value, Color) and isinstance(self.to_value, Color):
			value = Color()
			value.r = self.from_value.r + (self.to_value.r - self.from_value.r) * p
			value.g = self.from_value.g + (self.to_value.g - self.from_value.g) * p
			value.b = self.from_value.b + (self.to_value.b - self.from_value.b) * p
			value.a = self.from_value.a + (self.to_value.a - self.from_value.a) * p
			return value
		return 0.0


class Layer (object):	
	def __init__(self, rect=Rect()):
		self.frame = rect
		self.sublayers = list()
		self.animations = dict()
		self.scale_x = 1.0
		self.scale_y = 1.0
		self.rotation = 0.0
		self.image = None
		self.background = Color(0, 0, 0, 0)
		self.stroke = Color(0, 0, 0, 0)
		self.stroke_weight = 0.0
		self.tint = Color(1, 1, 1, 1)
		self.alpha = 1.0
		self.superlayer = None
		self.ignores_touches = False
	
	def _hit_test(self, location):
		if self.ignores_touches:
			return None
		if self.alpha <= 0:
			return None
			
		hit_layer = None
		if location in self.frame:
			hit_layer = self
		
		hit_sublayer = None
		for layer in self.sublayers:
			location_in_sublayer = Point(location.x - self.frame.x, location.y - self.frame.y)
			hit = layer._hit_test(location_in_sublayer)
			if hit: hit_sublayer = hit
			
		if hit_sublayer is not None:
			return hit_sublayer
		else:
			return hit_layer
	
	def convert_to_screen(self, location):
		tx = self.frame.x
		ty = self.frame.y
		l = self
		ancestor = l.superlayer
		while ancestor is not None:
			tx += ancestor.frame.x
			ty += ancestor.frame.y
			ancestor = ancestor.superlayer
		return Point(location.x + tx, location.y + ty)
	
	def convert_from_screen(self, location):
		tx = self.frame.x
		ty = self.frame.y
		l = self
		ancestor = l.superlayer
		while ancestor is not None:
			tx += ancestor.frame.x
			ty += ancestor.frame.y
			ancestor = ancestor.superlayer
		return Point(location.x - tx, location.y - ty)
	
	def update(self, dt):
		if (len(self.animations) > 0):
			for animation_key in self.animations.keys():
				#Note: It's possible that animations remove each other while updating
				if self.animations.has_key(animation_key): 
					animation = self.animations[animation_key]
					animation.update(dt)
			
		for s in self.sublayers:
			s.update(dt)
	
	def add_animation(self, animation, key):
		if animation.from_value == animation.to_value:
			return
		animation.attribute = key
		animation.layer = self
		self.animations[key] = animation
	
	def remove_animation(self, animation):
		del self.animations[animation.attribute]
	
	def remove_all_animations(self):
		self.animations = {}
	
	def add_layer(self, layer):
		if isinstance(layer, Layer):
			if layer != self:
				self.sublayers.append(layer)
				layer.superlayer = self
		else:
			raise TypeError('Invalid layer object')
	
	def remove_layer(self, layer=None):
		if layer is not None:
			try:
				self.sublayers.remove(layer)
			except ValueError:
				pass
		elif self.superlayer is not None:
			self.superlayer.remove_layer(self)
	
	def draw(self, a=1.0):
		a *= self.alpha
		if a <= 0: return
		
		push_matrix()
		frame = self.frame
		x = frame.x
		y = frame.y
		w = frame.w
		h = frame.h
		s_x = self.scale_x
		s_y = self.scale_y
		rot = self.rotation
		
		translate(x + w/2, y + h/2)
		if s_x != 1 or s_y != 1:
			scale(s_x, s_y)
			pass
		if rot != 0:
			rotate(rot)
			pass
		translate(-w * 0.5, -h * 0.5)
		
		bg = self.background
		bg_r = bg.r
		bg_g = bg.g
		bg_b = bg.b
		bg_a = bg.a
		
		strk = self.stroke
		strk_r = strk.r
		strk_g = strk.g
		strk_b = strk.b
		strk_a = strk.a * a
		
		fill(bg_r, bg_g, bg_b, bg_a * a)
		stroke(strk_r, strk_g, strk_b, strk_a)
		stroke_weight(self.stroke_weight)
		rect(0, 0, w, h)
		
		if self.image is not None:
			tint_color = self.tint
			if tint_color is not None:
				tint(tint_color.r, tint_color.g, tint_color.b, a)
			else:
				tint(1, 1, 1, a)
			image(self.image, 0, 0, w, h)
			
		for s in self.sublayers:
			s.draw(a)
		pop_matrix()
		
	
	def animate(self, attribute, to_value, duration=0.5, delay=0.0, curve=curve_sinodial, 
				repeat=1, autoreverse=False, completion=None):
		animation = Animation()
		animation.from_value = getattr(self, attribute)
		animation.to_value = to_value
		animation.duration = duration
		animation.delay = delay
		animation.curve = curve
		animation.completion = completion
		animation.autoreverse = autoreverse
		animation.repeat = repeat
		self.add_animation(animation, attribute)
			
class TextLayer (Layer):
  def __init__(self, text, font, font_size):
	Layer.__init__(self)
	img, size = render_text(text, font, font_size)
	self.image = img
	self.frame = Rect(0, 0, size.w, size.h)

class Button (Layer):
	def __init__(self, frame, title=None):
		Layer.__init__(self, frame)
		self.background = Color(0.9, 0.9, 0.9)
		self.stroke_weight = 2
		self.stroke = Color(0.5, 0.5, 0.5)
		self.action = None
		if title is not None:
			t = TextLayer(title, 'Helvetica-Bold', min(30, max(10, int(frame.h * 0.8))))
			t.ignores_touches = True
			t.tint = Color(0, 0, 0)
			t.frame.center(frame.w * 0.5, frame.h * 0.5)
			t.frame.x = int(t.frame.x)
			t.frame.y = int(t.frame.y)
			self.add_layer(t)
	
	def touch_began(self, touch):
		self.background = Color(0.7, 0.7, 0.7)
	
	def touch_moved(self, touch):
		if self.superlayer.convert_from_screen(touch.location) in self.frame:
			self.background = Color(0.7, 0.7, 0.7)
		else:
			self.background = Color(0.9, 0.9, 0.9)
	
	def touch_ended(self, touch):
		self.background = Color(0.9, 0.9, 0.9)
		if self.superlayer.convert_from_screen(touch.location) in self.frame:
			if callable(self.action):
				self.action()
	
