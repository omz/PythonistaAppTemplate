# This version of the getpass module was written specifically for the Pythonista
# UI. It only provides the getpass function (and not getuser, as iOS is not a 
# multi-user environment). Additionally, getpass has no stream parameter in this
# version.
#
# Author: Ole Zorn

import console

def getpass(prompt='Password: '):
	"""Prompt for a password.
	
	Args:
	  prompt: Written to the console to ask for input. Default: 'Password: '
	Returns:
	  The seKr3t input.
	"""
	
	password = console.secure_input(prompt)
	return password