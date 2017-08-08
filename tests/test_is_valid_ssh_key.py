from nisselib import is_valid_ssh_key

VALID_RSA_KEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCXt4B9t989k0f7PGbSwUHD7KvUoAwYQc3PST4VrAWsjnnmvnXmLUDrGjDGbSvY6E9TlDMZU35w0G6UigXeA4Xhf170B7IgX5EYf1uHwQoemjRRF3eoHCd8WFfqhVsAsAmYHpxP2BUAJ49LmcVS9uwfUw5fFlI97WMKc4nIdzigrmcMPvf8z/PpzrPbqi+PgxPlZJoj83tvqi+TlF+speJki4GpcC5K+lf3ZO8oDYK3s8E2KEHwO4VYRY1ftALVUFXXkGJAcK4jhyaBqFRLbUeT/smTlgec2PwtBZC9VW6wgvyEvW4fu9Y2Fogj6N1Rldnhc4l7JQMXM7KZDyVyzSDXum4Ynnrg6v6+eSGKq3/8+Y1cznNxfZ4DiDf5RhWVBriKwW7STVnlKKiQiQhETqqxa4KB5Zj3395jwCP4bSG9jtnhh2byjavBcIRtFpxnyR41A5SZ8ymdFXSsEZHs0LbaEnyu6DrA6nx8F6tJ5PigNxUXt84XULosQLJu/4zHJoYf4+6gU/+8v4EhpuVTq8J/4rg0tGbkR75j/ab+HBFXWlwVJift5H0gvYlHvqsKAAsYSLVcxk1EwZt1N3DrcCR2QlYKo11JstMjd+XnjnYz7NvAUTpejHUb2QxnkV7gpkr3rEeXyAvhfr1u2YjZMgUFSEgkMBNoHHfNDTO5pKaCdw== jordemoder@dikunix.dk
"""

VALID_DSA_KEY = """ssh-dss AAAAB3NzaC1kc3MAAACBAIogPPYOH4g2PPdHkpJmtrpotDwbM+KFw+Cj8hsbRXl74MMbaZoj0nhiqJ90YSfNligamrjV5V5CrbEP6S63UV3e733FtkE/w3/lJfOGZfgiUpeQGW6FXXAGJxov1D+qIpzlFpuiCl/zY2Ac6P7MNYCZrUD6GBmbCKqP8tZPs5r5AAAAFQDN6YjdGEc1MdMLBBzs1okLaP9zuQAAAIB+/4eGk2HKh17K0CxpnLKiJRNfLVqe0hzmNs6VONwuXy7iSsABg8enIrqrzGgV7iQtwcX+50+w3crgrXzK6WAlLH1NBrcRaJ1gpi7HAkrgtvTVHPlVWd17N5DDPq8/GPsR9ignUlpuL29dFi5rFS4IFR1SJyacjkiUcFS2OXRMQwAAAH91vHxa6fgiLbJlw7QWlknXbwgZHzRRwrrVNc3tT1RjtxqzQTvwOAYgvMpcXBLBgFV4N19eK1auJko77C82kbHYx2SNzMHAvp9qMwXtk4/TUN4X3ulicZTceTcAp6n1wfbsWl5IGOLD2J4S5t9NGJvduQZK1NUxC6YlMm/zJ3Vz jordemoder@dikunix.dk
"""

VALID_ED25519_KEY = """ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOsCsvx6J+e+cgd1PWDIwi6olI9B/kNkHzkz4HuXTBT6 jordemoder@dikunix.dk
"""

VALID_ECDSA_KEY = """ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBGx0of8/Z4sWaLG4lhG6zFgC8Mx7TN4Ao4RBU2fTiJ+QQUkdh6+IGWNAVVgDeh+NPzhpFDEpCY4VOdrAMfh5VWU= jordemoder@dikunix.dk
"""

def test_valid_rsa():
    assert is_valid_ssh_key(VALID_RSA_KEY)

def test_valid_dsa():
    assert is_valid_ssh_key(VALID_DSA_KEY)

def test_valid_ed25519():
    assert is_valid_ssh_key(VALID_ED25519_KEY)

def test_valid_ecdsa():
    assert is_valid_ssh_key(VALID_ECDSA_KEY)

def test_valid_key_with_trailing_line_breaks():
    assert is_valid_ssh_key(\
        VALID_RSA_KEY + \
        "\n\n")

def test_valid_multiple_keys():
    assert is_valid_ssh_key(\
        VALID_RSA_KEY + \
        VALID_DSA_KEY + \
        VALID_ED25519_KEY + \
        VALID_ECDSA_KEY)

def test_invalid_no_spaces():
    key = VALID_RSA_KEY.replace(' ', '')
    assert is_valid_ssh_key(key) == False

def test_invalid_no_type():
    key = ' '.join(VALID_RSA_KEY.split(' ')[1:])
    assert is_valid_ssh_key(key) == False
