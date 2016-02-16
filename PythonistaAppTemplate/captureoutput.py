def _capture_output_main():
	import _outputcapture
	import sys

	class StdoutCatcher (object):
		def __init__(self):
			self.encoding = 'utf8'
		def write(self, s):
			if isinstance(s, str):
				_outputcapture.CaptureStdout(s)
			elif isinstance(s, unicode):
				_outputcapture.CaptureStdout(s.encode('utf8'))
		def writelines(self, lines):
			for line in lines:
				self.write(line + '\n')
		def flush(self):
			pass

	class StderrCatcher (object):
		def __init__(self):
			self.encoding = 'utf8'
		def write(self, s):
			if isinstance(s, str):
				_outputcapture.CaptureStderr(s)
			elif isinstance(s, unicode):
				_outputcapture.CaptureStderr(s.encode('utf8'))
		def flush(self):
			pass

	class StdinCatcher (object):
		def __init__(self):
			self.encoding = 'utf8'
		def read(self, len=-1):
			return _outputcapture.ReadStdin(len)
		
		def readline(self):
			return _outputcapture.ReadStdin()

	sys.stdout = StdoutCatcher()
	sys.stderr = StderrCatcher()
	sys.stdin = StdinCatcher()

_capture_output_main()
del _capture_output_main
