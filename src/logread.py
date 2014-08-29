# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

import sys
import getopt
import string

from person import Person

def usage(cmd, error=None):
  if error is not None:
    print "Error: " + error

  print("USAGE HERE")

def verifyStr(toCheck, against):
  if set(toCheck) - set(against):
    return False
  else:
    return True

def enum(**enums):
  return type('Enum', (), enums)

LogReadAction = enum(
  state = 1, # -S
  rooms_by_person = 2, # -R
  time_by_person = 3, # -T
  rooms_occupied_simul = 4, # -I
  time_present = 5, # -A
  time_present_exclude = 6 # -B
)

def main(argv=None):
  if argv is None:
    argv = sys.argv

  if len(argv) == 0:
    usage("")
    return 1

  exe = argv[0]

  try:
    opt, tail = getopt.getopt(argv[1:], "K:HSRE:G:TABL:U:", ["help"])
  except getopt.error as err:
    usage(exe, err.msg)
    return 1

  # argument list
  opt_token = None
  opt_log = None
  opt_outputHtml = False
  opt_action = None
  opt_people = []
  opt_bounds = []

  # some temporary state
  seenLower = False
  lowerTmp = None

  for o,val in opt:
    if o == "--help":
      usage(exe)
      return 0
    elif o == "-K": # Token
      if not verifyStr(val, string.lowercase+string.uppercase+string.digits):
        usage(exe, "Token must match [a-zA-Z0-9]+")
        return 1

      opt_token = val
    elif o == "-E": # Token
      if not verifyStr(val, string.lowercase+string.uppercase):
        usage(exe, "Employee name must match [a-zA-Z]+")
        return 1

      opt_people.append(Person(val, False))
    elif o == "-G": # Token
      if not verifyStr(val, string.lowercase+string.uppercase):
        usage(exe, "Guest name must match [a-zA-Z]+")
        return 1

      opt_people.append(Person(val, True))
    elif o == "-L":
      if not verifyStr(val, string.digits):
        usage(exe, "Lower bound must be specified in seconds")
        return 1
      
      if seenLower:
        usage(exe, "Two lower bounds seen, but no upper in between!")
        return 1

      # we've seen a lower, now expect an upper
      seenLower = True
      lowerTmp = int(val, 10)
    elif o == "-U":
      if not verifyStr(val, string.digits):
        usage(exe, "Upper bound must be specified in seconds")
        return 1
      
      if not seenLower:
        usage(exe, "Saw an upper bound before a lower bound")
        return 1

      # we've seen an upper. we're done
      seenLower = False
      opt_bounds.append((lowertmp, int(val, 10)))
      lowerTmp = None 
    elif o == "-H":
      opt_outputHtml = True
    elif o == "-S": 
      if opt_action is not None:
        usage(exe, "the " + o + " option collides with another option")
        return 1

      opt_action = LogReadAction.state = 1 # -S
    elif o == "-R": 
      if opt_action is not None:
        usage(exe, "the " + o + " option collides with another option")
        return 1

      opt_action = LogReadAction.rooms_by_person = 2 # -R
    elif o == "-T": 
      if opt_action is not None:
        usage(exe, "the " + o + " option collides with another option")
        return 1

      opt_action = LogReadAction.time_by_person = 3 # -T
    elif o == "-I": 
      if opt_action is not None:
        usage(exe, "the " + o + " option collides with another option")
        return 1

      opt_action = LogReadAction.rooms_occupied_simul = 4 # -I
    elif o == "-A": 
      if opt_action is not None:
        usage(exe, "the " + o + " option collides with another option")
        return 1

      opt_action = LogReadAction.time_present = 5 # -A
    elif o == "-B": 
      if opt_action is not None:
        usage(exe, "the " + o + " option collides with another option")
        return 1

      opt_action = LogReadAction.time_present_exclude = 6 # -B

  # check for dangling, unmatched lower bounds
  if seenLower:
    usage(exe, "Done parsing args, but I never saw an upper bound for -L " + str(lowerTmp))
    return 1

  # we hope this is the log...
  if len(tail) > 0:
    opt_log = tail[0]

  if opt_log is None:
    usage(exe, "No log file specified")
    return 1

  if opt_token is None:
    usage(exe, "No token specified")
    return 1 

  if opt_action == LogReadAction.state:
    """log = LogFile(logFile, token)
    log.unseal()
    print log.dumpState()"""
    pass
  elif opt_action == LogReadAction.rooms_by_person:
    pass
  elif opt_action == LogReadAction.time_by_person:
    pass
  elif opt_action == LogReadAction.rooms_occupied_simul:
    pass
  elif opt_action == LogReadAction.time_present:
    pass
  elif opt_action == LogReadAction.time_present_exclude:
    pass
  else:
    usage(exe, "An action was never specified")
    return 1

  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv))
