import base64
import secrets

from hashlib import blake2b
from hmac import compare_digest

SCRYPT_N = 2 ** 14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 64
_SCHEME = "scrypt"


def _derive(secret, salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P):
  """Derive separate authentication and vault-encryption keys."""
  from Crypto.Protocol.KDF import scrypt

  derived = scrypt(
    secret,
    salt,
    key_len=SCRYPT_DKLEN,
    N=n,
    r=r,
    p=p,
  )
  return derived[:32], derived[32:]


def _parse_signature(sig):
  if isinstance(sig, bytes):
    sig = sig.decode("ascii")
  scheme, n, r, p, salt, verifier = sig.split("$", 5)
  if scheme != _SCHEME:
    raise ValueError("Unsupported password signature")
  n, r, p = int(n), int(r), int(p)
  if (n, r, p) != (SCRYPT_N, SCRYPT_R, SCRYPT_P):
    raise ValueError("Unsupported scrypt parameters")
  return (
    n,
    r,
    p,
    base64.urlsafe_b64decode(salt.encode("ascii")),
    base64.urlsafe_b64decode(verifier.encode("ascii")),
  )


def hash_sign(cookie, secret):
  """Create a slow, randomly salted password signature."""
  del cookie  # Retained in the API for compatibility with existing callers.
  salt = secrets.token_bytes(16)
  verifier, _ = _derive(secret, salt)
  salt_text = base64.urlsafe_b64encode(salt).decode("ascii")
  verifier_text = base64.urlsafe_b64encode(verifier).decode("ascii")
  return f"{_SCHEME}${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt_text}${verifier_text}".encode("ascii")


def is_legacy_signature(sig):
  if isinstance(sig, bytes):
    return not sig.startswith(f"{_SCHEME}$".encode("ascii"))
  return not str(sig).startswith(f"{_SCHEME}$")


def _legacy_hash(cookie, secret):
  h = blake2b(digest_size=32, key=secret)
  h.update(cookie)
  return h.hexdigest().encode("utf-8")

def verify(cookie, sig, secret):
  try:
    if is_legacy_signature(sig):
      return compare_digest(_legacy_hash(cookie, secret), sig)
    n, r, p, salt, expected = _parse_signature(sig)
    actual, _ = _derive(secret, salt, n=n, r=r, p=p)
    return compare_digest(actual, expected)
  except (TypeError, ValueError, UnicodeError):
    return False


def derive_vault_key(sig, secret):
  """Derive the in-memory key used to unwrap per-document keys."""
  n, r, p, salt, _ = _parse_signature(sig)
  _, vault_key = _derive(secret, salt, n=n, r=r, p=p)
  return vault_key

def hashed_id(pid):
  h = blake2b(digest_size=24)
  h.update(pid)
  return h.hexdigest().encode('utf-8')
