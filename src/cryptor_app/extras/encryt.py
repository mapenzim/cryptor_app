import base64
import secrets
from datetime import datetime

from cryptor_app.extras import generate_secrets
from cryptor_app.extras.models import (
  insertFile,
  retrieveFiles,
  retrieveSingleFile,
  updateFile,
)


KEY_FORMAT = b"v2:"


def _owner_name(session_cookie):
  return session_cookie.cookie_owner_username


def _wrap_file_key(vault_key, file_key):
  from Crypto.Cipher import AES

  cipher = AES.new(vault_key, AES.MODE_EAX)
  encrypted_key, tag = cipher.encrypt_and_digest(file_key)
  packed = cipher.nonce + tag + encrypted_key
  return KEY_FORMAT + base64.urlsafe_b64encode(packed)


def _unwrap_file_key(vault_key, wrapped_key):
  from Crypto.Cipher import AES

  if not isinstance(wrapped_key, bytes) or not wrapped_key.startswith(KEY_FORMAT):
    raise ValueError("Document does not contain a protected v2 key")
  packed = base64.urlsafe_b64decode(wrapped_key[len(KEY_FORMAT):])
  if len(packed) != 64:
    raise ValueError("Wrapped document key is malformed")
  nonce, tag, ciphertext = packed[:16], packed[16:32], packed[32:]
  return AES.new(vault_key, AES.MODE_EAX, nonce).decrypt_and_verify(ciphertext, tag)


def _encrypt_payload(plaintext, vault_key):
  from Crypto.Cipher import AES

  if not isinstance(vault_key, bytes) or len(vault_key) != 32:
    raise ValueError("The authenticated vault key is unavailable")
  file_key = secrets.token_bytes(32)
  cipher = AES.new(file_key, AES.MODE_EAX)
  ciphertext, tag = cipher.encrypt_and_digest(plaintext)
  wrapped_key = _wrap_file_key(vault_key, file_key)
  return ciphertext, cipher.nonce, tag, wrapped_key


def _decrypt_payload(docfile, vault_key, allow_legacy=False):
  from Crypto.Cipher import AES

  wrapped_key = docfile.session_key
  if isinstance(wrapped_key, bytes) and wrapped_key.startswith(KEY_FORMAT):
    file_key = _unwrap_file_key(vault_key, wrapped_key)
  elif allow_legacy and isinstance(wrapped_key, bytes):
    # Legacy files stored their raw AES key in this column. This path exists only
    # long enough to migrate an authenticated user's old records atomically.
    file_key = wrapped_key
  else:
    raise ValueError("This document still requires secure legacy migration")

  cipher = AES.new(file_key, AES.MODE_EAX, docfile.cipher_aes)
  return cipher.decrypt_and_verify(docfile.data_file, docfile.tag)


def prepare_legacy_migration(owner_name, vault_key):
  """Re-encrypt legacy rows in memory for one atomic database migration."""
  migrated = []
  for row in retrieveFiles(owner_name):
    wrapped_key = row[5]
    if isinstance(wrapped_key, bytes) and wrapped_key.startswith(KEY_FORMAT):
      continue

    doc = type("LegacyDocument", (), {
      "data_file": row[2],
      "cipher_aes": row[3],
      "tag": row[4],
      "session_key": wrapped_key,
    })()
    plaintext = _decrypt_payload(doc, vault_key, allow_legacy=True)
    ciphertext, nonce, tag, new_wrapped_key = _encrypt_payload(plaintext, vault_key)
    migrated.append({
      "file_id": row[0],
      "data_file": ciphertext,
      "cipher_aes": nonce,
      "tag": tag,
      "session_key": new_wrapped_key,
      "last_updated": datetime.now().isoformat(),
    })
  return migrated


def lock_file(
  session_cookie,
  upd_id,
  text_message,
  mode,
  file_title="Untitled",
  file_for="General",
  vault_key=None,
):
  if len(text_message) <= 5:
    return (
      "The text editor is blank or the characters are less than the required "
      "minimum number. Type something first to continue."
    )

  ciphertext, nonce, tag, wrapped_key = _encrypt_payload(
    text_message.encode("utf-8"),
    vault_key,
  )
  owner_name = _owner_name(session_cookie)

  if mode == "create":
    return insertFile(
      file_id=generate_secrets.hashed_id(secrets.token_bytes(24)),
      owner_name=owner_name,
      data_file=ciphertext,
      cipher_aes=nonce,
      tag=tag,
      session_key=wrapped_key,
      ts=datetime.now(),
      file_title=file_title,
      file_for=file_for,
    )

  if mode == "update":
    if upd_id is None or not upd_id.get():
      return "not_found"
    return updateFile(
      file_id=upd_id.get().encode("utf-8"),
      owner_name=owner_name,
      data_file=ciphertext,
      tag=tag,
      cipher_aes=nonce,
      session_key=wrapped_key,
      last_updated=datetime.now(),
      file_title=file_title,
      file_for=file_for,
    )

  return f"Unsupported file operation: {mode}"


def decrypt(doc_id, session_cookie, vault_key):
  if len(doc_id.get()) <= 1:
    raise ValueError("Select a document before attempting decryption")

  docfile = retrieveSingleFile(
    doc_id.get().encode("utf-8"),
    _owner_name(session_cookie),
  )
  if docfile is None:
    return "No content was found."

  plaintext = _decrypt_payload(docfile, vault_key)
  return plaintext.decode("utf-8")
