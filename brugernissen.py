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

import socket
import sys
import os
import stat
import re
import base64
import binascii
import struct
import subprocess

def is_valid_ssh_key(ssh_key):
    # All this is taken from https://gist.github.com/piyushbansal/5243418
    array=bytes(ssh_key, encoding='utf8').split()
    # Each rsa-ssh key has 3 different strings in it, first one being
    # typeofkey second one being keystring third one being username .
    if len(array) != 3:
        print(array)
        return False
    typeofkey=array[0]
    string=array[1]
    username=array[2];
    # must have only valid rsa-ssh key characters ie binascii characters
    try :
        data=base64.decodestring(string)
    except binascii.Error:
        print('b')
        return False
    a=4
    # unpack the contents of data, from data[:4], it must be equal to 7, property of ssh key .
    try :
        str_len = struct.unpack('>I', data[:4])[0]
    except struct.error :
        print('c')
        return false
    # data[4:11] must have string which matches with the typeofkey , another ssh key property.
    return data[4:4+str_len] == typeofkey and int(str_len) == int(7)

VALID_USERNAMES_REGEX='[a-zA-Z][a-zA-Z0-9]{0,20}'

def make_user(fd, username, ssh_key):
    if not re.match(VALID_USERNAMES_REGEX, username):
        fd.write('Username must match this regex: %s', VALID_USERNAMES_REGEX)
    elif not is_valid_ssh_key(ssh_key):
        fd.write('The given SSH key does not look like a valid SSH key.')
    else:
        secondary_group = 'dikunix'
        comment = 'En rus!'
        if subprocess.call(['useradd',
                            '-p', '',
                            '-G', secondary_group,
                            '-c', comment,
                            username]) != 0:
            fd.write('Failed to create user.')
        else:
            pass

def run_main():
    if len(sys.argv) != 2:
        sys.exit('Usage: %s <socket-filename>' % sys.argv[0])
    socketname = sys.argv[1]

    os.unlink(socketname)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(socketname)
    s.listen(1)

    print('Jeg står klar ved %s' % socketname)

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

            make_user(fd, username, ssh_key)
            fd.close()
            print('Endnu en kunde ekspederet!')
        except Exception as e:
            print('Unhandled exception: ' + str(e))

if __name__ == '__main__':
    try:
        run_main()
    except KeyboardInterrupt:
        pass
