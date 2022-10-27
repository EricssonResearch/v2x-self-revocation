import jwt
import random
import string
import math
from datetime import datetime, timezone

import conf

def generate_random_string(k = 16):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))

def decode_jwt(token):
    return jwt.api_jwt.decode_complete(token, options={
        "verify_signature": False,
        "verify_iss": False,
        "verify_aud": False,
        "verify_iat": False,
        "verify_nbf": False,
        "verify_exp": False
        })

def get_timestamp():
    return int(math.floor(datetime.now(timezone.utc).timestamp()))

def compute_remaining_time(t):
    now = get_timestamp()
    return conf.env("T_V") - (now - t)

def get_random_int(min_value, max_value):
    return random.randint(min_value, max_value)