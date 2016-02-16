import _motion

shared_manager = _motion.MotionManager()

def start_updates():
	shared_manager.start()

def stop_updates():
	shared_manager.stop()

def get_gravity():
	return shared_manager.gravity

def get_user_acceleration():
	return shared_manager.user_acceleration

def get_attitude():
	return shared_manager.attitude

def get_magnetic_field():
	return shared_manager.magnetic_field

class MotionUpdates (object):
	def __enter__(self):
		start_updates()
	
	def __exit__(self, type, value, traceback):
		stop_updates()
