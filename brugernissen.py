#!/usr/bin/env python3.5
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
import subprocess
import pwd
from nisselib import *


def make_user(fd, username, ssh_key):
    if not is_valid_username(username):
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
                            '-m',
                            username]) != 0:
            fd.write('Failed to create user.')
        else:
            with open('/home/%s/.ssh/authorized_keys' % username, 'w') as f:
                f.write(ssh_key)
            www_home = '/var/www/htdocs/dikunix.dk/~' + username
            if subprocess.call(['mkdir', www_home]) != 0 or \
                subprocess.call(['ln', '-s', www_home, 'public_html',
                cwd='/home/' + username]) != 0:
                fd.write('Failed to create dikunix.dk/~{}.'.format(username))

FRONTEND_USERNAME='athas'

def run_main():
    if len(sys.argv) != 2:
        sys.exit('Usage: %s <socket-filename>' % sys.argv[0])
    socketname = sys.argv[1]

    frontend_uid=pwd.getpwnam(FRONTEND_USERNAME)[2]

    try:
        os.unlink(socketname)
    except FileNotFoundError:
        pass
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(socketname)
    os.chown(socketname, frontend_uid, -1)
    os.chmod(socketname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
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
            fd.write('Internal error: ' + str(e))
            fd.close()

if __name__ == '__main__':
    try:
        run_main()
    except KeyboardInterrupt:
        pass
