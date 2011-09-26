# -*- coding: utf-8 -*-
import os

class Settings():

	date_format = "dd-MM-yyyy"
	date_time_format = "dd-MM-yyyy HH:mm"
	opts = None
	username = "root"
	password = "blastoff"
	__version__ = "1.0"
	
	def __init__(self):
		pass
	
	@staticmethod
	def version(self):
		return Settings.__version__
		

settings = Settings()
