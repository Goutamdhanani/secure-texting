import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Use env MASTER_KEY (32 bytes). For dev a default is provided but change in prod.
_master = os.getenv("MASTER_KEY", None)
if _master is None:
    # default for dev only: 32 ascii bytes
    MASTER_KEY = b"dev_master_key_32_bytes_long!!!!"
else:
    # allow passing raw 32-byte key or base64; here we expect raw bytes string
    MASTER_KEY = _master.encode() if isinstance(_master, str) else _master

def encrypt_message(plain_text: str):
    aes = AESGCM(MASTER_KEY)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, plain_text.encode("utf-8"), None)
    return ciphertext.hex(), nonce.hex()

def decrypt_message(cipher_hex: str, nonce_hex: str):
    aes = AESGCM(MASTER_KEY)
    pt = aes.decrypt(bytes.fromhex(nonce_hex), bytes.fromhex(cipher_hex), None)
    return pt.decode("utf-8")
