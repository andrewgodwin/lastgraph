#!/usr/bin/python

"""
A simple program to list some features of .last files
"""

from lastgui.storage import UserHistory

import sys, os

def usage():
	print >> sys.stderr, "Usage: %s <filename.last> <action>" % sys.argv[0]

try:
	filename = sys.argv[1]
except IndexError:
	usage()
	sys.exit(1)

try:
	action = sys.argv[2]
except IndexError:
	usage()
	sys.exit(1)

uh = UserHistory(None)
uh.load(open(filename))

if action == "artists":
	print "\n".join(uh.artists.keys())
elif action == "weeks":
	print "\n".join(map(str, uh.weeks.keys()))
elif action == "age":
	print uh.data_age()
else:
	print >> sys.stderr, "Unknown action"
	sys.exit(1)