import random
import string
import math
from datetime import datetime, timezone

def generate_random_id(k = 16):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))

def get_freshness_parameter():
    return int(math.floor(datetime.now(timezone.utc).timestamp()))

def read_from_file(filename):
    with open(filename, "r") as f:
        return f.read()