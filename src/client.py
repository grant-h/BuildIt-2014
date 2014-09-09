#!/usr/bin/env python
import os
import socket
import sys
import time

debug = False

def main(argv):
  # Create a UDS socket
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  retval = 0

  # Connect the socket to the port where the server is listening
  server_address = '/tmp/.logserver-socket.unix'

  # check to see if the server is running
  if not os.path.exists(server_address):
    pid = os.fork()

    if pid == 0: # child
      path =os.path.dirname(argv[0]) + "/logserver"
      print path
      os.execl(path, path)
    elif pid > 0:
      # wait for the server to be ready
      if debug:
        print "waiting"
      time.sleep(1)
      if not os.path.exists(server_address):
        print("Server failed to run")
        sys.exit(1)
    else:
      if debug:
        print("Failed to fork")

  if debug:
    print >>sys.stderr, 'connecting to %s' % server_address
  try:
    sock.connect(server_address)
  except socket.error, msg:
    if debug:
      print >>sys.stderr, msg
    return 1


  try:
    # Send data
    message = " ".join(argv)
    if debug:
      print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    output = ""

    while True:
      tmp = sock.recv(100)

      if tmp:
        output += tmp
      else:
        break

    if output != "":
      sep = output.find("\n")

      if sep == -1:
        retval = -1
      else:
        retval = int(output[:sep])

        if len(output) > sep+1:
          output = output[sep+1:]
          sys.stdout.write(output)
    else:
      retval = -1
  finally:
    if debug:
      print >>sys.stderr, 'closing socket'
      sock.close()

  return retval

if __name__ == "__main__":
  sys.exit(main(sys.argv))    
