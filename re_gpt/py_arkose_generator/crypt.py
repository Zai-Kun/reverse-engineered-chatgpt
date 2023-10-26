import base64
import hashlib
import json
import random

from Crypto.Cipher import AES


def pad(data):
    # Convert the string to bytes and calculate the number of bytes to pad
    data_bytes = data.encode()
    padding = 16 - (len(data_bytes) % 16)
    # Append the padding bytes with their value
    return data_bytes + bytes([padding] * padding)


def encrypt(data, key):
    salt = ""
    salted = ""
    dx = bytes()

    # Generate salt, as 8 random lowercase letters
    salt = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(8))

    # Our final key and IV come from the key and salt being repeatedly hashed
    for x in range(3):
        dx = hashlib.md5(dx + key.encode() + salt.encode()).digest()
        salted += dx.hex()

    # Pad the data before encryption
    data = pad(data)

    aes = AES.new(
        bytes.fromhex(salted[:64]), AES.MODE_CBC, bytes.fromhex(salted[64:96])
    )

    return json.dumps(
        {
            "ct": base64.b64encode(aes.encrypt(data)).decode(),
            "iv": salted[64:96],
            "s": salt.encode().hex(),
        }
    )
