#coding: utf-8

from _scene2 import *
import _scene2

from scene_drawing import *

import math
from numbers import Number
from io import BytesIO
import ui

DEFAULT_ORIENTATION = 0
PORTRAIT = 1
LANDSCAPE = 2

BLEND_NORMAL = 0
BLEND_ADD = 1
BLEND_MULTIPLY = 2

from ui import get_screen_size

def run(scene_to_run, orientation=0, frame_interval=1, anti_alias=False, show_fps=False, multi_touch=True):
	sv = SceneView()
	if orientation == PORTRAIT:
		ui_orientations = ['portrait']
	elif orientation == LANDSCAPE:
		ui_orientations = ['landscape']
	else:
		ui_orientations = None
	sv.anti_alias = anti_alias
	sv.frame_interval = frame_interval
	sv.multi_touch_enabled = multi_touch
	sv.shows_fps = show_fps
	sv.scene = scene_to_run
	sv.present(orientations=ui_orientations)

def gravity():
	g = _scene2.gravity()
	return Vector3(g[0], g[1], g[2])

class Touch (object):
	def __init__(self, x, y, prev_x, prev_y, touch_id):
		self.touch_id = touch_id
		self.location = Point(x, y)
		self.prev_location = Point(prev_x, prev_y)
		self.layer = None
		
	def __eq__(self, other_touch):
		if not isinstance(other_touch, Touch):
			return False
		elif other_touch.touch_id == self.touch_id:
			return True
		return False
	
	def __hash__(self):
		return self.touch_id.__hash__()

class Scene (SceneNode):
	def __init__(self, *args, **kwargs):
		SceneNode.__init__(self, *args, **kwargs)
		self.t = 0.0
		self.dt = 0.0
		self.root_layer = None
		self.touches = {}
		self.delayed_invocations = []
		w, h = ui.get_screen_size()
		self.size = Size(w, h)
		self.bounds = Rect(0, 0, w, h)
		self.presented_scene = None
		self.presenting_scene = None
		self.setup_finished = False
		
	def setup(self):
		pass
	
	def update(self):
		pass
	
	def did_evaluate_actions(self):
		pass
	
	def draw(self):
		pass
	
	def did_change_size(self):
		pass
	
	def stop(self):
		pass
	
	def pause(self):
		pass
	
	def resume(self):
		pass
	
	def touch_began(self, touch):
		pass
	
	def touch_moved(self, touch):
		pass
	
	def touch_ended(self, touch):
		pass
	
	def present_modal_scene(self, other_scene):
		if self.presented_scene:
			self.dismiss_modal_scene()
		other_scene._setup_scene(*self.size)
		other_scene._set_size(*self.size)		
		self.presented_scene = other_scene
		other_scene.presenting_scene = self
		other_scene.z_position = max(n.z_position for n in self.children) + 1
		self.add_child(other_scene)
	
	def dismiss_modal_scene(self):
		if self.presented_scene:
			self.presented_scene.presenting_scene = None
			self.presented_scene.remove_from_parent()
			self.presented_scene = None
		elif self.presenting_scene:
			self.presenting_scene.dismiss_modal_scene()
	
	def add_layer(self, layer):
		if self.root_layer is None:
			s = self.size
			self.root_layer = Layer(Rect(0, 0, s[0], s[1]))
		self.root_layer.add_layer(layer)
	
	def delay(self, dt, func):
		invocation = { 't': self.t + dt, 'f': func }
		self.delayed_invocations.append(invocation)
	
	def _setup_scene(self, width, height):
		if hasattr(self, 'setup_finished') and self.setup_finished:
			return
		self.size = Size(width, height)
		self.bounds = Rect(0, 0, width, height)
		
		# Note: Some legacy code relies on not having to call super in __init__, so these are initialized again here...
		self.t = 0.0
		self.dt = 0.0
		self.root_layer = None
		self.touches = {}
		self.delayed_invocations = []
		self.presented_scene = None
		self.presenting_scene = None
		
		self.setup()
		self.setup_finished = True
	
	def _set_size(self, width, height):
		if self.size.w != width or self.size.h != height:
			self.size = Size(width, height)
			self.bounds = Rect(0, 0, width, height)
			self.crop_rect = self.bounds
			self.did_change_size()
		if self.presented_scene:
			self.presented_scene._set_size(width, height)
	
	def should_rotate(self, orientation):
		return False
	
	def _process_delayed_invocations(self):
		fired_invocations = None
		for invocation in self.delayed_invocations:
			if invocation['t'] <= self.t:
				invocation['f']()
				if fired_invocations is None:
					fired_invocations = []
				fired_invocations.append(invocation)
		if fired_invocations is not None:
			for invocation in fired_invocations:
				self.delayed_invocations.remove(invocation)
	
	def _draw(self, dt):
		paused = self.paused
		
		if not paused:
			self.dt = dt
			self.t += dt
		
		self._process_delayed_invocations()
		self.draw()
		if not paused:
			self.update()
			
		self._update(dt)
		
		if not paused:
			self.did_evaluate_actions()
		
		self._render()
		
		if self.presented_scene:
			self.presented_scene._draw(dt)
		
	def _stop(self):
		self.stop()
	
	def _touch_began(self, x, y, touch_id):
		if self.presented_scene:
			self.presented_scene._touch_began(x, y, touch_id)
			return
		touch = Touch(x, y, x, y, touch_id)
		if self.root_layer is not None:
			hit_layer = self.root_layer._hit_test(Point(x, y))
			touch.layer = hit_layer
			if hit_layer is not None:
				if hasattr(hit_layer, 'touch_began') and callable(hit_layer.touch_began):
					hit_layer.touch_began(touch)
		self.touches[touch_id] = touch
		self.touch_began(touch)

	def _touch_moved(self, x, y, prev_x, prev_y, touch_id):
		if self.presented_scene:
			self.presented_scene._touch_moved(x, y, prev_x, prev_y, touch_id)
			return
		touch = Touch(x, y, prev_x, prev_y, touch_id)
		old_touch = self.touches.get(touch_id, None)
		if old_touch is not None:
			touch.layer = old_touch.layer
			if touch.layer is not None:
				if hasattr(touch.layer, 'touch_moved') and callable(touch.layer.touch_moved):
					touch.layer.touch_moved(touch)
		self.touches[touch_id] = touch
		self.touch_moved(touch)

	def _touch_ended(self, x, y, touch_id):
		if self.presented_scene:
			self.presented_scene._touch_ended(x, y, touch_id)
			return
		touch = Touch(x, y, x, y, touch_id)
		old_touch = self.touches.get(touch_id, None)
		if old_touch is not None:
			del self.touches[touch_id]
			touch.layer = old_touch.layer
			if touch.layer is not None:
				if hasattr(touch.layer, 'touch_ended') and callable(touch.layer.touch_ended):
					touch.layer.touch_ended(touch)
		self.touch_ended(touch)


class LabelNode (SpriteNode):
	def __init__(self, text='', font=('Helvetica', 20), *args, **kwargs):
		SpriteNode.__init__(self, *args, **kwargs)
		self._suspend_updates = True
		self._rendered_text = None
		self.text = text
		self.font = font
		self._suspend_updates = False
		self.update_texture()
	
	def __setattr__(self, name, value):
		SpriteNode.__setattr__(self, name, value)
		if name == 'font':
			try:
				if len(value) != 2:
					raise TypeError('Expected a sequence of font name and size')
				if not isinstance(value[0], basestring):
					raise TypeError('Font name must be a string')
				if not isinstance(value[1], Number):
					raise TypeError('Font size must be a number')
			except TypeError:
				raise TypeError('Expected a sequence of font name and size')
		if name == 'font' or (name == 'text' and value != self._rendered_text):
			self.update_texture()
		
	def update_texture(self):
		if self._suspend_updates:
			return
		w, h = ui.measure_string(self.text, font=self.font)
		
		with ui.ImageContext(max(w, 1), max(h, 1)) as ctx:
			ui.draw_string(self.text, (0, 0, w, h), self.font, color='white')
			img = ctx.get_image()
		self.texture = Texture(img)
		self._rendered_text = self.text


class ShapeNode (SpriteNode):
	def __init__(self, path=None, fill_color='white', stroke_color='clear', shadow=None, *args, **kwargs):
		SpriteNode.__init__(self, *args, **kwargs)
		self._suspend_updates = True
		self.path = path
		self.line_width = path.line_width
		self.fill_color = fill_color
		self.stroke_color = stroke_color
		self.shadow = shadow
		self._suspend_updates = False
		self.update_texture()
	
	def __setattr__(self, name, value):
		SpriteNode.__setattr__(self, name, value)
		if name == 'line_width':
			self.path.line_width = value
			self.update_texture()
		if name in ('path', 'fill_color', 'stroke_color', 'shadow'):
			self.update_texture()
		
	def update_texture(self):
		if self._suspend_updates or not self.path:
			return
			
		if self.shadow:
			shadow_color = self.shadow[0]
			shadow_offset_x = self.shadow[1]
			shadow_offset_y = self.shadow[2]
			shadow_radius = self.shadow[3]
		else:
			shadow_offset_x = 0
			shadow_offset_y = 0
			shadow_radius = 0
			
		shadow_left = shadow_radius - shadow_offset_x
		shadow_right = shadow_radius + shadow_offset_x
		shadow_top = shadow_radius - shadow_offset_y
		shadow_bottom = shadow_radius + shadow_offset_y
		
		lw = self.path.line_width
		path_bounds = self.path.bounds
		w = max(1, math.ceil(path_bounds.w + abs(shadow_left) + abs(shadow_right)) + lw)
		h = max(1, math.ceil(path_bounds.h + abs(shadow_top) + abs(shadow_bottom)) + lw)
		
		with ui.ImageContext(w, h) as ctx:
			ui.concat_ctm(ui.Transform.translation(lw/2 + max(0, shadow_left) - path_bounds.x, lw/2 + max(0, shadow_top) - path_bounds.y))
			ui.set_color(self.fill_color)
			with ui.GState():
				if self.shadow:
					ui.set_shadow(shadow_color, shadow_offset_x, shadow_offset_y, shadow_radius)
				self.path.fill()
			if self.path.line_width > 0:
				ui.set_color(self.stroke_color)
				self.path.stroke()
			img = ctx.get_image()
		self.texture = Texture(img)
