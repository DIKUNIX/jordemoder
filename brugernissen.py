#!/usr/bin/env python3.5
# encoding: utf8
#
# Create new Unix users in response to requests on a Unix domain
# socket.
#
# Create a socket at a given location.  On this socket, we read
# requests for user creation: one line for the user name, another for
# the public SSH key.  This program must run as root, because it adds
# users by calling `adduser`.

import StringIO
import socket
import sys
import os
import stat

def run_main():
    if len(sys.argv) != 2:
        sys.exit("Usage: %s <socket-filename>" % sys.argv[0])
    socketname = sys.argv[1]

    os.unlink(socketname)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(socketname)
    s.listen(1)

    while True:
        try:
            conn, addr = s.accept()
            print('Der er en der banker på.')
            fd = conn.makefile(mode='rw')
            conn.close() # fd keeps the socket alive.
            username = fd.readline().strip()
            ssh_key = fd.readline().strip()

            print('Jeg er blevet bedt om at lave en bruger der hedder %s og som har SSH-nøglen %s' %
                  (username, ssh_key))
            fd.write('Alletiders')
            fd.close()
            print('Endnu en kunde ekspederet!')
        except Exception as e:
            print('Unhandled exception: ' + str(e))

if __name__ == '__main__':
    try:
        run_main()
    except KeyboardInterrupt:
        pass
