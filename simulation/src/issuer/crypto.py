from jwcrypto import jwk, jwe
import os
import binascii

def encrypt(key, data):
    public_key = jwk.JWK()
    public_key.import_from_pem(key)

    protected_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256CBC-HS512",
        "typ": "JWE",
        "kid": public_key.thumbprint(),
    }

    jwetoken = jwe.JWE(
        data,
        recipient=public_key,
        protected=protected_header
    )

    return jwetoken.serialize(compact=True)

def generate_group_key():
    return binascii.hexlify(os.urandom(16)).decode("utf-8")