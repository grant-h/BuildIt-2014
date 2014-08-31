# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

from room import Room

class Person(object):
  name = ""
  guest = None
  room = Room() # assume outside

  def __init__(self, name, guest):
    self.name = name
    self.guest = guest
    self.room = Room()

  def __str__(self):
    return self.name

  def __eq__(self, other):
    return self.name == other.name
