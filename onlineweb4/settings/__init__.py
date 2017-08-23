import sys
import os

if not os.path.exists(os.path.join(os.path.dirname(globals()['__file__']), 'base.py')):
    sys.stderr.write("Failed to locate the base settings file. Quitting.\n")
    sys.exit(1)
try:
    from onlineweb4.settings.base import *
except ImportError as e:
    sys.stderr.write("Failed to import from the base settings file. Quitting.\n" + str(e) + "\n")
    sys.exit(1)
