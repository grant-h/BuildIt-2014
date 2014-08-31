# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

from types import *

class Room(object):
  number = None # -1 used for foyer, None for outside
  people = []

  FOYER = -1

  # assume the "room" is outside
  def __init__(self, number=None):
    if number is None:
      self.number = None
    else:
      assert type(number) is IntType and number >= -1
      self.number = number

  def __str__(self):
    if self.isFoyer():
      return "Foyer"
    elif self.isOutside():
      return "Outside"
    else:
      return str(self.number)

  def __eq__(self, other):
    return other.number == self.number

  def serialize(self):
    assert self.number != None

    return str(self.number)

  def isFoyer(self):
    return self.number == -1

  def isOutside(self):
    return self.number is None

  def isInside(self):
    return not self.isOutside()

  def isRoom(self):
    return self.isInside() and not self.isFoyer()

  def addPerson(self, person):
    self.people.append(person)

  def removePerson(self, person):
    self.people.remove(person)

  def getPeopleSorted(self, person):
    return sorted(self.people, key=lambda p: p.name)

  def getNumPeople(self):
    return self.people.count()
