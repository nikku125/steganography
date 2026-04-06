"""
Cryptography Module for the Steganography Tool.
Provides AES-128 encryption/decryption with PBKDF2 key derivation,
SHA-256 integrity hashing, and secure salt generation.
"""

import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256


# --- Configuration ---
SALT_SIZE = 16        # 16 bytes = 128 bits
AES_KEY_SIZE = 16     # 16 bytes = AES-128
AES_BLOCK_SIZE = 16   # AES block size in bytes
IV_SIZE = 16          # Initialization vector size
PBKDF2_ITERATIONS = 100_000  # Key derivation iterations


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return os.urandom(SALT_SIZE)


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive an AES-128 key from a password using PBKDF2-HMAC-SHA256.

    Args:
        password: The user-supplied password string.
        salt: A 16-byte random salt.

    Returns:
        A 16-byte derived key suitable for AES-128.
    """
    key = PBKDF2(
        password.encode('utf-8'),
        salt,
        dkLen=AES_KEY_SIZE,
        count=PBKDF2_ITERATIONS,
        hmac_hash_module=SHA256
    )
    return key


def compute_sha256(data: bytes) -> str:
    """
    Compute the SHA-256 hash of data for integrity verification.

    Args:
        data: The data to hash.

    Returns:
        Hex-encoded SHA-256 digest string.
    """
    return hashlib.sha256(data).hexdigest()


def encrypt(plaintext: bytes, password: str) -> bytes:
    """
    Encrypt data using AES-128-CBC with PBKDF2-derived key.

    Payload format:
        [salt (16 bytes)] [iv (16 bytes)] [sha256 hash (32 bytes hex = 64 bytes)] [ciphertext]

    Args:
        plaintext: The raw data to encrypt.
        password: The user-supplied password for key derivation.

    Returns:
        The encrypted payload with salt, IV, and integrity hash prepended.
    """
    # Generate salt and derive key
    salt = generate_salt()
    key = derive_key(password, salt)

    # Compute integrity hash of the original plaintext
    integrity_hash = compute_sha256(plaintext).encode('utf-8')  # 64 bytes

    # Generate random IV and encrypt
    iv = os.urandom(IV_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES_BLOCK_SIZE))

    # Combine: salt + iv + integrity_hash + ciphertext
    return salt + iv + integrity_hash + ciphertext


def decrypt(payload: bytes, password: str) -> tuple:
    """
    Decrypt an AES-128-CBC encrypted payload and verify integrity.

    Args:
        payload: The encrypted payload (salt + iv + hash + ciphertext).
        password: The user-supplied password for key derivation.

    Returns:
        A tuple of (decrypted_data: bytes, integrity_valid: bool).

    Raises:
        ValueError: If the payload is too short or decryption fails
                    (e.g., wrong password).
    """
    min_size = SALT_SIZE + IV_SIZE + 64  # salt + iv + sha256 hex hash
    if len(payload) < min_size:
        raise ValueError("Encrypted payload is too short or corrupted.")

    # Extract components
    salt = payload[:SALT_SIZE]
    iv = payload[SALT_SIZE:SALT_SIZE + IV_SIZE]
    stored_hash = payload[SALT_SIZE + IV_SIZE:SALT_SIZE + IV_SIZE + 64].decode('utf-8')
    ciphertext = payload[SALT_SIZE + IV_SIZE + 64:]

    # Derive key and decrypt
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        plaintext = unpad(cipher.decrypt(ciphertext), AES_BLOCK_SIZE)
    except (ValueError, KeyError) as e:
        raise ValueError(
            "Decryption failed. Wrong password or corrupted data."
        ) from e

    # Verify integrity
    computed_hash = compute_sha256(plaintext)
    integrity_valid = (computed_hash == stored_hash)

    return plaintext, integrity_valid
