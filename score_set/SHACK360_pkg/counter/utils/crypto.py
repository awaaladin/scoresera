from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def get_fernet():
    key = getattr(settings, 'MASTER_KEY', None)
    if not key:
        return None
    # Assume the key is a URL-safe base64-encoded 32-byte key string
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def encrypt_text(plaintext: str) -> str:
    f = get_fernet()
    if not f:
        raise RuntimeError('MASTER_KEY not configured')
    return f.encrypt(plaintext.encode()).decode()


def decrypt_text(token: str) -> str:
    f = get_fernet()
    if not f:
        raise RuntimeError('MASTER_KEY not configured')
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        # If token invalid, raise to let caller handle (or return original)
        raise


def encrypt_with_key(plaintext: str, key: bytes) -> str:
    """Encrypt plaintext using a provided Fernet key (bytes or str)."""
    if isinstance(key, str):
        key = key.encode()
    f = Fernet(key)
    return f.encrypt(plaintext.encode()).decode()


def decrypt_with_key(token: str, key: bytes) -> str:
    """Decrypt token using provided Fernet key (bytes or str)."""
    if isinstance(key, str):
        key = key.encode()
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()
