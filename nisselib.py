import base64
import binascii
import struct
import re


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
def is_valid_username(username):
    return re.fullmatch(VALID_USERNAMES_REGEX, username)
