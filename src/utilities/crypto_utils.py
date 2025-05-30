# crypto_utils.py
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_key() -> bytes:
    """Generate a secure 128-bit key for AES-GCM."""
    return AESGCM.generate_key(bit_length=128)

def encrypt_data(key: bytes, plaintext: bytes, associated_data: bytes = None) -> (bytes, bytes):
    """Encrypt data using AES-GCM, returns nonce and ciphertext."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce, ciphertext

def decrypt_data(key: bytes, nonce: bytes, ciphertext: bytes, associated_data: bytes = None) -> bytes:
    """Decrypt data using AES-GCM."""
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data)

