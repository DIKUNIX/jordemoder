import base64
import re
from sshpubkeys import SSHKey, InvalidKeyException


def is_valid_ssh_key(ssh_key):
    ssh = SSHKey(ssh_key)
    try:
        ssh.parse()
    except (InvalidKeyException, NotImplementedError):
        return False
    return True


VALID_USERNAMES_REGEX='[a-zA-Z][a-zA-Z0-9]{0,20}'
def is_valid_username(username):
    return re.fullmatch(VALID_USERNAMES_REGEX, username)
