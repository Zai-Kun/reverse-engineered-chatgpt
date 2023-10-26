import struct

import mmh3


def x64hash128(data, seed=0):
    hash_bytes = mmh3.hash_bytes(data, seed=seed, x64arch=True)
    hash_hex = struct.unpack("<QQ", hash_bytes)
    hash_hex_str = "{:016x}{:016x}".format(*hash_hex)

    return hash_hex_str
