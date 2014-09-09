# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

import sys

DEBUG = False

def debug():
  return DEBUG

def verifyStr(toCheck, against):
  if set(toCheck) - set(against):
    return False
  else:
    return True

def enum(**enums):
  return type('Enum', (), enums)

def pdebug(msg):
  if DEBUG:
    sys.stderr.write("DEBUG: " + msg + "\n")

def die(msg, extra_msg=None, retVal=-1):
  if extra_msg is not None and DEBUG:
    pdebug(extra_msg)

  sys.stdout.write(msg + "\n")
  sys.exit(retVal)

