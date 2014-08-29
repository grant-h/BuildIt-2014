# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

from common import *

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

  def __str__(self):
    eventStr = ""

    if self.eventType == EventType.Arrival:
      eventStr = "arrive"
    else:
      eventStr = "depart"

    return "[%d, %s, %s, %s]" % (self.timestamp, eventStr, self.person, self.room)
