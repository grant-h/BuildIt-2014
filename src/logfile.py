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

  maxTime = -1
  events = []
  # mappings of names to people
  guests = dict()
  employees = dict()
  rooms = dict()  # int(roomID) : Person
  
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
      """self.createNew()

      try:
        fp = open(self.logPath, "rb")
      except IOError, err:
        die("invalid", "Created the log file, but I can't open it!")

      fp.close()"""
      return True

    # read that junk in to memory
    # TODO FIXME: prevent multiple readers...
    fileData = fp.read()
    fp.close()

    # TODO
    # Verify HMAC
    # Verify Nonce to check for modification by logappend
    # Unencrypt
    # Uncompress
    # Unserialize
    # read the file state in to memory
    #   parseFile(fileData)

    # WARNING JANK CODE ALERT
    lines = fileData.split("\n")

    # verify that the first line is our token
    if lines[0] != self.token:
      die("security error", "Failed to match token against saved file")

    # read in the events
    for l in lines[1:]:
      if l == "":
        continue

      if not self.parseEvent(l):
        die("invalid", "Corrupt event line: " + l)

    return True

  def parseEvent(self, event):
    evt = Event.deserialize(event)

    if evt is None:
      return False

    if evt.eventType == EventType.Arrival:
      self.arrival(evt.timestamp, evt.person, evt.room)
    elif evt.eventType == EventType.Departure:
      self.departure(evt.timestamp, evt.person, evt.room)

    return True

  # for each event, seal it up in our target file
  def seal(self):
    fp = None

    """self.createNew()

    try:
      fp = open(self.logPath, "rb")
    except IOError, err:
      die("invalid", "Created the log file, but I can't open it!")

    fp.close()"""

    try:
      fp = open(self.logPath, "wb")
    except IOError, e:
      die("invalid", "Could not reseal the file")

    fp.write(self.token + "\n")

    for e in self.events:
      fp.write(e.serialize() + "\n")

    fp.close()

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

  def rmPerson(self, person):
    if person.guest:
      del self.guests[person.name]
    else:
      del self.employees[person.name]

  def dump(self):
    pdebug("DUMP")
    for i in self.events:
      pdebug(str(i))

  def dumpState(self, html):
    outstr = ""
    empList = sorted(self.employees.items(), key=lambda e: e[0]) 
    empList = [i[0] for i in empList]

    guestList = sorted(self.guests.items(), key=lambda e: e[0])
    guestList = [i[0] for i in guestList]

    roomList = sorted(self.rooms.items(), key=lambda e: e[0])
    peopleList = []

    # flatten the list of lists
    for num,peep in roomList:
      peopleList.append(",".join(sorted([i.name for i in peep])))

    # make room list just a bunch of numbers
    roomList = [i[0] for i in roomList]

    if html:
      outstr += "<html><body>"
      outstr += self.genHTMLTable(['Employee', 'Guest'], [empList, guestList])
      outstr += self.genHTMLTable(['Room ID', 'Occupants'], [roomList, peopleList])
      outstr += "</html></body>"
    else:
      outstr += ",".join(empList) + "\n"
      outstr += ",".join(guestList) + "\n"

      for i,num in enumerate(roomList):
        outstr += "%d: " % (num) + peopleList[i] + "\n"

    return outstr

  def genHTMLTable(self, colList, rows):
    header = "<tr>"
    body = ""
    numCols = len(colList)
    numRows = -1 # inf

    for i in rows:
      numRows = max(len(i), numRows)

    # generate header
    for i in colList:
      header += "<th>" + i + "</th>"

    header += "</tr>"

    # generate data cells
    for i in xrange(numRows):
      body += "<tr>"

      for data in rows:
        if len(data) > i:
          body += "<td>" + str(data[i]) + "</td>"

      body += "</tr>"

    return "<table>" + header + body + "</table>"

  def getRoomsEnteredBy(self, person, html):
    rms = []

    for e in self.events:
      num = e.room.number
      if person == e.person and num >= 0 and num not in rms:
        rms.append(e.room.number)

    rms = [str(s) for s in rms]

    if html:
      outstr = "<html><body>"
      outstr += self.genHTMLTable(['Rooms'], [rms])
      outstr += "</body></html>"

      return outstr
    else:
      return ','.join(str(s) for s in rms)

  # ------ Event State Management -------
  def arrival(self, time, person, room):
    if time <= self.maxTime:
      die("invalid", "Attempted to add event with lower than or equal time")

    # look up the miscreant
    realPerson = self.lookupPerson(person)

    # person isnt in the gallery right now. they can arrive in the foyer
    if realPerson is None and room.isFoyer():
      self.addPerson(person)
      return self.appendEvent(time, EventType.Arrival, person, room)
    # person is here already
    elif realPerson is not None:
      return self.appendEvent(time, EventType.Arrival, realPerson, room)
    # everything else is wrong
    else:
      die("invalid", str(person) + " tried to break in")

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

  def appendEvent(self, time, eventType, person, dstRoom):
    # it is assumed we have a person object
    curRoom = person.room
    event = None

    # outside -> foyer
    if curRoom.isOutside() and dstRoom.isFoyer() and eventType == EventType.Arrival:
      person.room = dstRoom  # welcome to the gallery
      event = Event(time, eventType, person, dstRoom)
    # foyer -> room
    elif curRoom.isFoyer() and dstRoom.isRoom() and eventType == EventType.Arrival:
      person.room = dstRoom 

      if dstRoom.number not in self.rooms:
        self.rooms.update({dstRoom.number : [person]})
      else:
        self.rooms[dstRoom.number].append(person)

      event = Event(time, eventType, person, dstRoom)
    # room -> foyer
    elif curRoom.isRoom() and dstRoom == curRoom and eventType == EventType.Departure:
      person.room = Room(Room.FOYER) # enter the foyer again

      # delete person from room
      peepList = self.rooms[curRoom.number] # list of strs
      peepList.remove(person)

      if len(peepList) == 0:
        del self.rooms[curRoom.number]

      event = Event(time, eventType, person, dstRoom)
    # foyer -> outside
    elif curRoom.isFoyer() and dstRoom.isFoyer() and eventType == EventType.Departure:
      person.room = Room() # go outside
      self.rmPerson(person)

      # checking...
      assert self.lookupPerson(person) is None

      event = Event(time, eventType, person, dstRoom)
    else:
      die("invalid", str(person) + " is bending space time. Nab him! (%s -> %s)" %
          (str(curRoom), str(dstRoom)))

    self.events.append(event)
