#!/usr/bin/python

import argparse
import os
import shutil
import sys

argparser = argparse.ArgumentParser(description='A script to copy this template with the specified Python script')
argparser.add_argument('script', type=str,
						help='Script that copied template will contain')
argparser.add_argument('path', type=str, help='File path of copied template')
args = argparser.parse_args()

script = os.path.abspath(os.path.expanduser(args.script))
path = os.path.abspath(os.path.expanduser(args.path))
assert os.path.isfile(script) and script.endswith('.py'), 'script must be valid Python script'
#assert os.path.isdir(path), 'path must be a valid directory'
print('Script: ' + script)
print('Path to copy to: ' + path)
print('OK? (Y/n)')
response = raw_input()
if response == '' or response.lower() == 'y':
	print('Copying...')
	shutil.copytree(os.path.realpath(__file__[:-15]), path)
	os.chdir(path + '/Script')     
	print('Changing script...')
	os.remove('./main.py')
	shutil.copy(script, './main.py')
	print('Template successfully copied!')
	
else:
	print('Cancelled.')
	sys.exit(0)