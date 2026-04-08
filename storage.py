"""Load and save accounts to an encrypted local file."""

import json
import os
from typing import List, Dict, Any

from crypto import encrypt, decrypt

DATA_FILE = "accounts.dat"


def load_accounts(key: bytes) -> List[Dict[str, Any]]:
    """Load accounts from *DATA_FILE* decrypted with *key*.

    Returns an empty list when the file does not exist yet.
    Raises ``cryptography.fernet.InvalidToken`` when the key is wrong.
    """
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "rb") as f:
        token = f.read()
    plaintext = decrypt(token, key)
    return json.loads(plaintext.decode())


def save_accounts(accounts: List[Dict[str, Any]], key: bytes) -> None:
    """Encrypt *accounts* with *key* and write to *DATA_FILE*."""
    plaintext = json.dumps(accounts, ensure_ascii=False).encode()
    token = encrypt(plaintext, key)
    with open(DATA_FILE, "wb") as f:
        f.write(token)
