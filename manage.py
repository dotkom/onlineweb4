#!/usr/bin/env python
import os
import sys

import threading; threading.stack_size(4*80*1024)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onlineweb4.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
