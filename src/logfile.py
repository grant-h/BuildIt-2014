# Build it, Break it, Fix it 2014 Submission
#  Written by team KnightSec

from common import *
from eventstate import EventState

# import win
from Crypto.Hash import HMAC,SHA256
from Crypto.Cipher import AES 
from Crypto.Protocol.KDF import PBKDF2 
from Crypto import Random

# file format constants
MAGIC = "BIBI"
HMAC_LEN = SHA256.digest_size
IV_LEN = AES.block_size
HMAC_SALT_LEN = 16
ENC_SALT_LEN = 16

class LogFile(object):
  logPath = None
  token = None

  # some event stats
  state = None # actual gallery state handler
  newLogFile = False
  unsealed = False
  initialNumEvents = 0

  # cryptographic data
  hmacSalt = ""
  encryptSalt = ""
  encryptIV = ""
  hmacKey = ""
  encryptionKey = ""

  def __init__(self, logPath, token): 
    self.logPath = logPath
    self.token = token

  # Would prefer a KDF as per the research here
  # http://palms.ee.princeton.edu/PALMSopen/yao05design.pdf
  # It looks like PyCrypto already strengthens PBKDF2 a bit
  # using XOR and appending the current iteration count
  def hmac(self, msg):
    # use SHA256 instead of MD5
    return HMAC.new(self.hmacKey, msg, SHA256).digest()

  def enc(self, msg):
    aes = AES.new(self.encryptionKey, AES.MODE_CBC, self.encryptIV)

    BS = AES.block_size
    padLen = BS - len(msg) % BS
    pad = lambda m: m+padLen*chr(padLen) 

    # let the caller decide what to do with the IV
    return aes.encrypt(pad(msg))

  def dec(self, msg):
    unpad = lambda m: m[0:-ord(m[-1])]

    aes = AES.new(self.encryptionKey, AES.MODE_CBC, self.encryptIV)
    plaintext = aes.decrypt(msg)

    return unpad(plaintext)

  def unseal(self, secure=True):
    fp = None

    try:
      fp = open(self.logPath, "rb")
      self.newLogFile = False
    except IOError, err:
      pdebug("No log file found. Starting with blank event state")
      self.newLogFile = True

      # start with a blank state
      self.state = EventState()
      self.unsealed = True
      self.initialNumEvents = 0

      return self.state

    # read that junk in to memory
    fileData = fp.read()
    fp.close()

    # ----- File Layout -----
    # SECURE: 
    # BIBI[HMAC (16 bytes)][HMAC Salt][Encrypt Salt][IV][Encrypted Blob]
    # 
    # [Encrypted Blob] -- <DECRYPT> --> [Raw Events]
    #
    # INSECURE:
    # [Raw Events] = [EventLine]\n .. [EventLine]\n
    # EventLine = [timestamp],[arrive/leave (1 byte)],[name],[isguest],[room#]

    if secure:
      HEADER_LEN = len(MAGIC) + HMAC_LEN + HMAC_SALT_LEN + ENC_SALT_LEN + IV_LEN

      if len(fileData) < HEADER_LEN: 
        die("invalid", "Not enough space for file header")

      # Check for the magic \o/ *^*^*^*^*!
      if fileData[0:4] != MAGIC:
        die("invalid", "Invalid magic bytes found")

      ptr = len(MAGIC)

      # Read the HMAC
      hmac = fileData[ptr:ptr+HMAC_LEN]
      ptr += HMAC_LEN 

      # Grab the HMAC salt
      self.hmacSalt = fileData[ptr:ptr+HMAC_SALT_LEN]
      ptr += HMAC_SALT_LEN 

      # Grab the encrypt salt
      self.encryptSalt = fileData[ptr:ptr+HMAC_SALT_LEN]
      ptr += ENC_SALT_LEN

      # Read the IV off the byte stream
      self.encryptIV = fileData[ptr:ptr+IV_LEN]
      ptr += IV_LEN

      assert ptr == HEADER_LEN

      # Cut off the header
      encBlob = fileData[ptr:]

      # Using our salts and token, derive the keys to perform the checks
      self.hmacKey = PBKDF2(self.token, self.hmacSalt)
      self.encryptionKey = PBKDF2(self.token, self.encryptSalt)

      # Generate the HMAC
      tryHmac = self.hmac(encBlob)

      if hmac != tryHmac:
        die("security error", "Integrity of the encrypted container failed to be verified")

      # Decrypt
      fileData = self.dec(encBlob)

    lines = fileData.split("\n")

    try:
      self.state = EventState(lines)
      self.unsealed = True
      self.initialNumEvents = len(self.state.events)

      return self.state
    except ValueError, e:
      die("invalid", e.message)

  # for each event, seal it up in our target file
  def seal(self, secure=True):

    if not self.unsealed:
      return

    # check to see if anything was changed
    # no need to write anything if nothing was changed
    if len(self.state.events) == self.initialNumEvents:
      return

    fp = None

    try:
      # was this the first time the file has been written to?
      if self.newLogFile: # WARNING: race condition, check again and lock XXX
        # TODO: lock the file for writing
        fp = open(self.logPath, "wb")

      # we should just append a new event to the log file
      # no need to rewrite the entire thing
      else:
        fp = open(self.logPath, "wb") # for now...
        #fp = open(self.logPath, "ab")

        # Goal: seek backwards enough encrypted chunks
        # until we can completely recover the last event line.
        # Then, write the last event line and any extraneous data
        # and append our new event(s)
        #fp.seek(security
    except IOError, e:
      die("invalid", "Could not modify the log file: " + e.strerror)

    flatLog = "" 
    dataOut = ""

    for e in self.state.events:
      flatLog += e.serialize() + "\n"

    if secure:
      # generate our salts and keys if needed
      if self.newLogFile:
        randGen = Random.new()
        self.hmacSalt = randGen.read(HMAC_SALT_LEN)
        self.encryptSalt = randGen.read(ENC_SALT_LEN)
        self.encryptIV = randGen.read(IV_LEN)

        self.hmacKey = PBKDF2(self.token, self.hmacSalt)
        self.encryptionKey = PBKDF2(self.token, self.encryptSalt)

      # Encrypt the flat log file
      encLog = self.enc(flatLog)

      # Calculate the HMAC
      hmac = self.hmac(encLog)

      # Concatenate all of our files
      dataOut = MAGIC + hmac + self.hmacSalt + \
        self.encryptSalt + self.encryptIV + encLog
    else:
      dataOut = flatLog
      
    try:
      fp.write(dataOut) # could be locked
      fp.close()

      self.newLogFile = False
    except IOError:
      die("invalid", "Failed to write data back to the database")
