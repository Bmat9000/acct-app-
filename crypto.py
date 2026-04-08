"""Encryption and decryption helpers using Fernet + PBKDF2HMAC."""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT_FILE = "salt.bin"
# OWASP recommends ≥ 480 000 iterations for PBKDF2-HMAC-SHA256 (as of 2023)
ITERATIONS = 480_000


def load_or_create_salt() -> bytes:
    """Return the saved salt, creating a new random one on first run."""
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            return f.read()
    salt = os.urandom(16)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    return salt


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from *password* and *salt*."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(data: bytes, key: bytes) -> bytes:
    """Return *data* encrypted with *key*."""
    return Fernet(key).encrypt(data)


def decrypt(token: bytes, key: bytes) -> bytes:
    """Return decrypted bytes, or raise ``InvalidToken`` on wrong key."""
    return Fernet(key).decrypt(token)
