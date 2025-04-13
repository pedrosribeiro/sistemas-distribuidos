from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def load_private_key(path: str):
    with open(path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )


def load_public_key(path: str):
    with open(path, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(), backend=default_backend()
        )


def sign_message(message: bytes, private_key):
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())


def verify_signature(message: bytes, signature: bytes, public_key):
    try:
        public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        return False
