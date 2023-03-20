from datetime import datetime, timezone
import math
import jwt
import aiohttp

def get_timestamp():
    return int(math.floor(datetime.now(timezone.utc).timestamp()))

def decode_jwt(token):
    return jwt.api_jwt.decode_complete(token, options={
        "verify_signature": False,
        "verify_iss": False,
        "verify_aud": False,
        "verify_iat": False,
        "verify_nbf": False,
        "verify_exp": False
        })

def get_payload(data):
    token = decode_jwt(data)
    return token["payload"]

async def revoke_pseudonym(ps):
    async with aiohttp.ClientSession("http://ra") as session:
        try:
            async with session.get(f'/revoke/{ps}') as response:
                return await response.text(), response.status
        except Exception as e:
            return f"Exception: {e}", 500

async def get_heartbeat(session):
    try:
        async with session.get(f'/heartbeat') as response:
            return get_payload(await response.text()), response.status
    except Exception as e:
        return f"Exception: {e}", 500