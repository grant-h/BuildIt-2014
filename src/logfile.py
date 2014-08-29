class LogFile(object):
  logPath = None
  token = None
  people = []
  guests = []
  employees = []
  rooms = []
  
  def __init__(self, logPath, token): 
    self.logPath = filePath
    self.token = token

  def unseal(self):
    try:
      fp = open(self.logPath, "rb")
    except IOError, err:
      print("Error while opening log file: " + err.msg)
      return False

    # read that junk in to memory
    # TODO FIXME: prevent multiple readers...
    fileData = fp.read()
    fp.close()

    # Verify HMAC
    # Unencrypt
    # Uncompress
    # Unserialize
    # Parse data
