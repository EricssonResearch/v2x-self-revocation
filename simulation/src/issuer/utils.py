import random
import string
import aiohttp

def generate_random_id(k = 16):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))

async def get_freshness_parameter():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://ra/freshness') as response:
            if response.status != 200:
                raise Exception(f"Freshness request failed: {response.status}")
            
            return int((await response.text()).encode())

def read_from_file(filename):
    with open(filename, "r") as f:
        return f.read()