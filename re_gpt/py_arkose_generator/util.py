import base64
import json
import random
import time
import urllib.parse

from .crypt import encrypt
from .fingerprint import getEnhancedFingerprint, getFingerprint, prepareF, prepareFe
from .murmur import x64hash128

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"


def _random():
    hex_chars = "0123456789abcdef"
    random_string = "".join(random.choice(hex_chars) for _ in range(32))
    return random_string


def constructFormData(data):
    filtered_data = {k: v for k, v in data.items() if v is not None}
    encoded_data = [
        f"{k}={urllib.parse.quote(str(v))}" for k, v in filtered_data.items()
    ]
    form_data = "&".join(encoded_data)
    return form_data


def getBda(userAgent, opts):
    fp = getFingerprint()
    fe = prepareFe(fp)

    bda = [
        {"key": "api_type", "value": "js"},
        {"key": "p", "value": 1},
        {"key": "f", "value": x64hash128(prepareF(fp), 31)},
        {
            "key": "n",
            "value": base64.b64encode(str(int(time.time())).encode()).decode("utf-8"),
        },
        {"key": "wh", "value": f"{_random()}|{_random()}"},
        {"key": "enhanced_fp", "value": getEnhancedFingerprint(fp, userAgent, opts)},
        {"key": "fe", "value": fe},
        {"key": "ife_hash", "value": x64hash128(", ".join(fe), 38)},
        {"key": "cs", "value": 1},
        {
            "key": "jsbd",
            "value": json.dumps(
                {"HL": 4, "DT": "", "NWD": "false", "DOTO": 1, "DMTO": 1}
            ),
        },
    ]

    current_time = int(time.time())
    key = userAgent + str(current_time - (current_time % 21600))
    s = json.dumps(bda)
    encrypted = encrypt(s, key)

    return base64.b64encode(encrypted.encode()).decode("utf-8")
