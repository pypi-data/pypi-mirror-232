
'''
	from botanist.SYSTEM.ADD_PATHS import ADD_PATHS_TO_SYSTEM

	ADD_PATHS_TO_SYSTEM ([ 'THIS_MODULE' ])
'''
def ADD_PATHS_TO_SYSTEM (PATHS):
	import pathlib
	FIELD = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	for PATH in PATHS:
		sys.path.insert (0, normpath (join (FIELD, PATH)))

