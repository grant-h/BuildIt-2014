# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

from common import *
from person import Person
from room import Room

EventType = enum(
  Arrival = 1,
  Departure = 2,
)

class Event(object):
  timestamp = None
  eventType = None
  person = None
  room = None

  def __init__(self, timestamp, eventType, person, room):
    self.timestamp = timestamp
    self.eventType = eventType
    self.person = person
    self.room = room

  def serialize(self):
    return "%d,%d,%s,%d,%s" % \
      (self.timestamp, self.eventType, self.person.name, self.person.guest, self.room.serialize())

  @classmethod
  def deserialize(cls, data):
    tokens = data.split(",")

    # deserialize
    if len(tokens) != 5:
      return None

    # TODO: more verification
    timestamp = int(tokens[0])
    eventType = int(tokens[1])
    name = tokens[2]
    guest = int(tokens[3])

    person = Person(name, guest)
    room = Room(int(tokens[4]))

    return cls(timestamp, eventType, person, room)

  def __str__(self):
    eventStr = ""

    if self.eventType == EventType.Arrival:
      eventStr = "arrive"
    else:
      eventStr = "depart"

    return "[%d, %s, %s, %s]" % (self.timestamp, eventStr, self.person, self.room)
