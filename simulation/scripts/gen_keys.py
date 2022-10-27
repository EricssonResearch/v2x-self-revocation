from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

k = ec.generate_private_key(curve=ec.SECP256R1())

priv_serialized = k.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode("utf-8")

pub_serialized = k.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

with open("cred/ra_private.pem", "w") as f:
    f.write(priv_serialized)

with open("cred/ra_public.pem", "w") as f:
    f.write(pub_serialized)