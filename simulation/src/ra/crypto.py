import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import \
    load_pem_private_key, load_pem_public_key

class Ecdsa():
    def __init__(self, signing_key=None, verifying_key=None):
        if signing_key is None and verifying_key is None:
            self.signing_key = ec.generate_private_key(curve=ec.SECP384R1())
            self.verifying_key = self.signing_key.public_key()
        else:
            self.signing_key = signing_key
            self.verifying_key = verifying_key

    def load(signing_key_path=None, verifying_key_path=None):
        sk = None
        vk = None

        if signing_key_path is not None:
            with open(signing_key_path, "rb") as f:
                sk_pem = f.read()
            sk = load_pem_private_key(sk_pem, password=None)

        if verifying_key_path is not None:
            with open(verifying_key_path, "rb") as f:
                vk_pem = f.read()
            vk = load_pem_public_key(vk_pem)
        elif sk is not None:
            vk = sk.public_key()

        return Ecdsa(sk, vk)
            
    def sign(self, data):
        return self.signing_key.sign(data, ec.ECDSA(hashes.SHA256()))

    def verify(self, data, signature):
        return self.verifying_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))

    def sign_jwt(self, data, algorithm="ES256"):
        return jwt.encode(data, self.signing_key, algorithm=algorithm)

    def verify_jwt(self, data, algorithms=["ES256"]):
        return jwt.decode(data, self.verifying_key, algorithms=algorithms)