# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

from types import *

class Room(object):
  number = None
  mainHall = True

  def __init__(self, number=None):
    if number is None:
      self.number = None
      self.mainHall = True
    else:
      assert type(number) is IntType and number >= 0
      self.number = number
      self.mainHall = False

  def __str__(self):
    if self.isFoyer():
      return "Foyer"
    else:
      return str(self.number)

  def __eq__(self, other):
    return other.number == self.number and other.isFoyer() == self.isFoyer()

  def isFoyer(self):
    return self.mainHall
