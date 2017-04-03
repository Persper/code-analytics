#!/usr/bin/env python3

import os
import subprocess
import git

def main():
	print('The patch is generated for gitpython release 2.1.1.')
	print('Your gitpython version is {}'.format(git.__version__))
	src_file = os.path.join(os.path.dirname(git.__file__), 'diff.py')
	cmd = 'patch {} < gitpython.diff'.format(src_file)
	subprocess.call(cmd, shell=True)

if __name__ == '__main__':
	main()