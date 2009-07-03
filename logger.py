import logging
import os

LEVELS = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR, 'critical': logging.CRITICAL}

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

class Logger(object):
	def __init__(self, level='error', output='stream', file=None):
		log = logging.getLogger('MtGLogger')
		log.setLevel(LEVELS[level])
		
		handler = None
		if output == 'stream':
			handler = logging.StreamHandler()
		else:
			if file is None:
				file = os.path.join(os.path.dirname(__file__), 'log.log')
			handler = logging.FileHandler(file)
			
		self.file = file
		self.handler = handler
			
		formatter = logging.Formatter("|%(relativeCreated)5d | %(name)-10s | %(levelname)-10s | %(message)s")
		handler.setFormatter(formatter)
		log.addHandler(handler)
		
		self.log_instance = log
		
	def log(self, message, level='debug'):
		getattr(self.log_instance, level)(message)
		
	def change_level(self, level='debug'):
		global LEVELS
		
		self.log_instance.setLevel(LEVELS[level])
		
	def no_logging(self):
		self.log_instance.removeHandler(self.handler)

		null_handler = NullHandler()
		self.log_instance.addHandler(null_handler)
		self.handler = null_handler