# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

from common import *

from room import Room
from logevent import Event,EventType
from person import Person

class LogFile(object):

  logPath = None
  fileHandle = None
  token = None

  maxTime = 0
  events = []
  # mappings of names to people
  guests = dict()
  employees = dict()
  rooms = []
  
  def __init__(self, logPath, token): 
    self.logPath = logPath
    self.token = token

  """
  createNew(token):

  Create a new file in memory and a blank one on disk.
  Uses the specified token to create the file.
  """
  def createNew(self):
    try:
      fp = open(self.logPath, "wb")
    except IOError, err:
      die("invalid", "Failed to create new log file")

    # hold the file handle to prevent other writers
    fileHandle = fp

    # no events
    self.events = []

  def unseal(self):
    fp = None

    try:
      fp = open(self.logPath, "rb")
    except IOError, err:
      pdebug("No log file found. Creating new one...")
      self.createNew()

      try:
        fp = open(self.logPath, "rb")
      except IOError, err:
        die("invalid", "Created the log file, but I can't open it!")

    # read that junk in to memory
    # TODO FIXME: prevent multiple readers...
    fileData = fp.read()
    fp.close()

    # Verify HMAC
    # Verify Nonce to check for modification by logappend
    # Unencrypt
    # Uncompress
    # Unserialize
    # Parse data

    # read the file state in to memory
    #parseFile(fileData)

    return True

  def lookupPerson(self, person):
    if person.guest:
      return self.guests.get(person.name)
    else:
      return self.employees.get(person.name)

  def addPerson(self, person):
    if person.guest:
      return self.guests.update({person.name : person})
    else:
      return self.employees.update({person.name : person})

  def arrival(self, time, person, room):
    if time <= self.maxTime:
      die("invalid", "Attempted to add event with lower than or equal time")

    # look up the miscreant
    realPerson = self.lookupPerson(person)

    # person isnt in the gallery right now. they can arrive
    if realPerson is None and room.isFoyer():
      self.addPerson(person)
      return self.appendEvent(time, EventType.Arrival, person, room)
    elif realPerson is not None:
      return self.appendEvent(time, EventType.Arrival, realPerson, room)
    # everything else is wrong
    else:
      die("invalid", realPerson + " tried to break in")

  def departure(self, time, person, room):
    if time <= self.maxTime:
      die("invalid", "Attempted to add event with lower than or equal time")

    # whoareyou
    realPerson = self.lookupPerson(person)

    # they cant leave if they arent here
    if realPerson is None:
      die("invalid", "Person tried to leave but isnt here")
    else:
      # person is in the gallery right now. they can move about
      return self.appendEvent(time, EventType.Departure, realPerson, room)

  def dump(self):
    print("DUMP")
    for i in self.events:
      print(i)

  def appendEvent(self, time, eventType, person, room):
    curRoom = person.room

    # outside -> foyer
    if curRoom is None and room.isFoyer():
      person.room = room 
      self.events.append(Event(time, eventType, person, room))
    # foyer -> room
    elif curRoom.isFoyer() and not room.isFoyer() and eventType == EventType.Arrival:
      person.room = room 
      self.events.append(Event(time, eventType, person, room))
    # room -> foyer
    elif not curRoom.isFoyer() and room == curRoom and eventType == EventType.Departure:
      person.room = Room() # enter the foyer again
      self.events.append(Event(time, eventType, person, room))
    # foyer -> outside
    elif curRoom.isFoyer() and room.isFoyer() and eventType == EventType.Departure:
      person.room = Room() # go outside
      self.events.append(Event(time, eventType, person, room))
    else:
      die("invalid", str(person) + " is bending space time. Nab him! (%s -> %s)" %
          (curRoom, room))

    self.dump()
