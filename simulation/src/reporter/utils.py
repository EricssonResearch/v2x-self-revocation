import jwt
import random

import conf

def decode_jwt(token):
    return jwt.api_jwt.decode_complete(token, options={
        "verify_signature": False,
        "verify_iss": False,
        "verify_aud": False,
        "verify_iat": False,
        "verify_nbf": False,
        "verify_exp": False
        })

def get_iss(data):
    token = decode_jwt(data)
    return token["payload"]["iss"]

def roll_dice(p):
    return random.random() < p

def get_random_int(min_value, max_value):
    return random.randint(min_value, max_value)

def get_random_element(elements):
    return random.choice(elements)

def compute_delay_time():
    return random.randint(1, conf.env("T_V"))