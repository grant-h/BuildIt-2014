# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

import sys
import getopt
import string
import types

from common import *
from room import Room
from person import Person
from logfile import LogFile
from eventstate import EventState,EventType

PersonAction = enum(
  Arrive = 1, # -A
  Depart = 2, # -L
)

def usage(cmd, error=None):
  DEBUG = True
  output = ""
  
  if error is not None and DEBUG:
    output += "Error: " + error + "\n"

  if DEBUG:
    output += """Usage:
    %s -T <timestamp> -K <token> (-E <employee-name> | -G <guest-name>) (-A | -L) [-R <room-id>] <log>
    %s -B <file>
    """ % (cmd, cmd)
  else:
    output += "invalid"

  return (output, -1)

def main(argv=None):
  if argv is None:
    argv = sys.argv

  if len(argv) == 0:
    return usage("")

  exe = argv[0]

  opt_batchfile = None
  batchMode = False

  # just check for a batch file
  try:
    opt, tail = getopt.getopt(argv[1:], "B:")

    for o,val in opt:
      if o == "-B": # enter batch mode
        opt_batchfile = val
        batchMode = True

    if len(tail) > 0 and batchMode:
      return usage(exe, "Batch file passed with extra options")
  except getopt.error as err:
    batchMode = False

  if not batchMode:
    return parse_cmd(exe, argv[1:])
  else:
    fp = None

    try:
      fp = open(opt_batchfile, "r")
    except IOError, err:
      return ("Could not open batch file \'%s\' for reading: %s" %
          (opt_batchfile, err.strerror), 1)

    # split the lines
    commands = fp.read().split("\n")
    fp.close()

    # get a life
    if len(commands) == 0:
      return usage(exe, "Passed in an empty batchfile...what are you doing with your life?")

    totalOutput = ""
    retVal = 0

    for i in commands:
      if i == "":
        continue

      # create our new argv
      newArgv = i.split()

      # keep the last retval
      (output, retVal) = parse_cmd(exe, newArgv)
      totalOutput = "%s%s" % (totalOutput, output)

    return (totalOutput, retVal)

def parse_cmd(exe, argv):
  try:
    opt, tail = getopt.getopt(argv, "T:K:B:E:G:ALR:", ["help"])
  except getopt.error as err:
    return usage(exe, err.msg)

  # option values
  opt_log = None
  opt_token = None
  opt_timestamp = None
  opt_roomid = Room(Room.FOYER) # assume Foyer
  opt_people = []
  opt_action = None

  for o,val in opt:
    if o == "--help":
      return usage(exe)
    elif o == "-B": # deny batch mode
      return die("invalid", "Batch file passed along with other options")
    elif o == "-K":
      if not verifyStr(val, string.lowercase+string.uppercase+string.digits):
        return usage(exe, "Token must match [a-zA-Z0-9]+")

      opt_token = val
    elif o == "-T":
      if not verifyStr(val, string.digits):
        return usage(exe, "Timestamp must be a number")

      opt_timestamp = int(val, 10)

      if opt_timestamp < 0:
        return usage(exe, "Timestamp must be non-negative")
    elif o == "-E":
      if not verifyStr(val, string.lowercase+string.uppercase):
        return usage(exe, "Employee name must match [a-zA-Z]+")

      opt_people.append(Person(val, False))
    elif o == "-G":
      if not verifyStr(val, string.lowercase+string.uppercase):
        return usage(exe, "Guest name must match [a-zA-Z]+")

      opt_people.append(Person(val, True))
    elif o == "-R":
      if not verifyStr(val, string.digits):
        return usage(exe, "Room ID must be a number")

      opt_roomid = Room(int(val, 10))

      if opt_roomid < 0:
        return usage(exe, "Room ID must be non-negative")
    elif o == "-A":
      if opt_action is not None:
        return usage(exe, "Person's direction was already specified. Requested action would cause tearing.")

      opt_action = PersonAction.Arrive
    elif o == "-L":
      if opt_action is not None:
        return usage(exe, "Person's direction was already specified. Requested action would cause tearing.")
      opt_action = PersonAction.Depart

  if opt_timestamp is None:
    return usage(exe, "No timestamp specified")

  # we hope this is the log...
  if len(tail) > 0:
    opt_log = tail[0]

  if opt_log is None:
    return usage(exe, "No log file specified")

  if opt_token is None:
    return usage(exe, "No token specified")

  if len(opt_people) == 0:
    return usage(exe, "No person specified")
  elif len(opt_people) > 1:
    return usage(exe, "Too many people moving around at once")

  log = LogFile(opt_log, opt_token)
  state = log.unseal()
  result = None

  if type(state) == types.TupleType:
    return state

  if opt_action == PersonAction.Arrive:
    result = state.arrival(opt_timestamp, opt_people[0], opt_roomid)
  elif opt_action == PersonAction.Depart:
    result = state.departure(opt_timestamp, opt_people[0], opt_roomid)
  else:
    return usage(exe, "An action was never specified")

  log.seal()

  return result 

if __name__ == "__main__":
  sys.exit(main(sys.argv))
