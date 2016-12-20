#!/usr/bin/env python3.5
# encoding: utf8
#
# A client program to test brugernissen.py.

import socket
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit("Usage: %s <socket-filename> <username> <ssh-key>" % sys.argv[0])
    filename = sys.argv[1]
    username = sys.argv[2]
    ssh_key = sys.argv[3]
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(filename)
        fd = s.makefile(mode='rw')
        fd.write(username + '\n' + ssh_key + '\n')
        fd.flush()
        resp=fd.read()
        print('Response: ' + resp)
    except socket.error as msg:
        print('Connection error: ' + str(msg), file=sys.stderr)
        sys.exit(1)
