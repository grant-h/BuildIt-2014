class Person(object):
  name = ""
  guest = None

  def __init__(self, name, isGuest):
    self.name = name
    self.guest = isGuest

  def __str__(self):
    return self.name
