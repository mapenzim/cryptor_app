import os
import sqlite3 as sql
from collections import namedtuple
from datetime import datetime
from functools import wraps


db_path = os.path.expanduser("~/.cryptor_app/notebookserver.db")


def time_stuff(some_function):
  @wraps(some_function)
  def wrapper(*args, **kwargs):
    return some_function(*args, **kwargs)
  return wrapper


def namedtuple_factory(cursor, row):
  fields = [column[0] for column in cursor.description]
  cls = namedtuple("Row", fields)
  return cls._make(row)


def _connect(named_rows=False):
  con = sql.connect(os.path.realpath(db_path))
  if named_rows:
    con.row_factory = namedtuple_factory
  return con


def _timestamp(value):
  return value.isoformat() if isinstance(value, datetime) else value


@time_stuff
def insertUser(user_id, username, password, timestamp):
  con = _connect()
  try:
    with con:
      con.execute(
        """
        INSERT INTO users(user_id, user_name, password, ts, last_updated, cookie)
        VALUES(:user_id, :user_name, :password, :ts, :last_updated, :cookie)
        """,
        {
          "user_id": user_id,
          "user_name": username,
          "password": password,
          "ts": _timestamp(timestamp),
          "last_updated": _timestamp(timestamp),
          "cookie": False,
        },
      )
    return "success"
  except Exception as exc:
    return exc
  finally:
    con.close()


@time_stuff
def insertCookie(
  cookie_id,
  cookie_owner_id,
  cookie_owner_username,
  ts,
  cookie_expire_time,
  cookie_owner_ts,
  cookie_owner_last_updated,
  cookie_expired=False,
):
  """Create one exact session and invalidate every older active session."""
  con = _connect(named_rows=True)
  try:
    with con:
      con.execute("UPDATE cookies SET cookie_expired = 1 WHERE cookie_expired = 0")
      con.execute(
        """
        INSERT INTO cookies(
          cookie_id, cookie_owner_id, cookie_owner_username, ts,
          cookie_expire_time, cookie_owner_ts, cookie_owner_last_updated,
          cookie_expired
        ) VALUES(
          :cookie_id, :cookie_owner_id, :cookie_owner_username, :ts,
          :cookie_expire_time, :cookie_owner_ts, :cookie_owner_last_updated,
          :cookie_expired
        )
        """,
        {
          "cookie_id": cookie_id,
          "cookie_owner_id": cookie_owner_id,
          "cookie_owner_username": cookie_owner_username,
          "ts": _timestamp(ts),
          "cookie_expire_time": _timestamp(cookie_expire_time),
          "cookie_owner_ts": _timestamp(cookie_owner_ts),
          "cookie_owner_last_updated": _timestamp(cookie_owner_last_updated),
          "cookie_expired": cookie_expired,
        },
      )
      return con.execute(
        "SELECT * FROM cookies WHERE cookie_id = :cookie_id",
        {"cookie_id": cookie_id},
      ).fetchone()
  finally:
    con.close()


@time_stuff
def verifyCookie(cookie_id=None):
  """Return the newest unexpired cookie, optionally constrained by exact ID."""
  con = _connect(named_rows=True)
  try:
    if cookie_id is None:
      rows = con.execute(
        "SELECT * FROM cookies WHERE cookie_expired = 0 ORDER BY ts DESC"
      ).fetchall()
    else:
      rows = con.execute(
        """
        SELECT * FROM cookies
        WHERE cookie_expired = 0 AND cookie_id = :cookie_id
        ORDER BY ts DESC
        """,
        {"cookie_id": cookie_id},
      ).fetchall()

    now = datetime.now()
    for cookie in rows:
      try:
        expires = datetime.fromisoformat(str(cookie.cookie_expire_time))
      except (TypeError, ValueError):
        expires = datetime.min
      if expires > now:
        return cookie
      with con:
        con.execute(
          "UPDATE cookies SET cookie_expired = 1 WHERE cookie_id = :cookie_id",
          {"cookie_id": cookie.cookie_id},
        )
    return None
  finally:
    con.close()


def expire_all_cookies():
  con = _connect()
  try:
    with con:
      con.execute("UPDATE cookies SET cookie_expired = 1 WHERE cookie_expired = 0")
  finally:
    con.close()


def searchUser(user_name):
  con = _connect(named_rows=True)
  try:
    return con.execute(
      "SELECT * FROM users WHERE user_name = :user_name",
      {"user_name": user_name},
    ).fetchone()
  except Exception:
    return "ERROR"
  finally:
    con.close()


@time_stuff
def logout_func(cookie_id):
  con = _connect()
  try:
    with con:
      cur = con.execute(
        "UPDATE cookies SET cookie_expired = 1 WHERE cookie_id = :cookie_id",
        {"cookie_id": cookie_id},
      )
    return cur.rowcount == 1
  finally:
    con.close()


@time_stuff
def renew_cookie(cookie_id, cookie_expire_time):
  con = _connect()
  try:
    with con:
      cur = con.execute(
        """
        UPDATE cookies
        SET cookie_expire_time = :cookie_expire_time
        WHERE cookie_id = :cookie_id AND cookie_expired = 0
        """,
        {
          "cookie_expire_time": _timestamp(cookie_expire_time),
          "cookie_id": cookie_id,
        },
      )
    return cur.rowcount == 1
  finally:
    con.close()


def retrieveUsers():
  con = _connect()
  try:
    return con.execute("SELECT user_name, password FROM users").fetchall()
  finally:
    con.close()


@time_stuff
def insertFile(
  file_id,
  owner_name,
  data_file,
  cipher_aes,
  tag,
  session_key,
  ts,
  file_title,
  file_for,
):
  con = _connect()
  try:
    with con:
      con.execute(
        """
        INSERT INTO lockedfiles(
          file_id, owner_name, data_file, cipher_aes, tag, session_key,
          ts, last_updated, file_title, file_for
        ) VALUES(
          :file_id, :owner_name, :data_file, :cipher_aes, :tag, :session_key,
          :ts, :last_updated, :file_title, :file_for
        )
        """,
        {
          "file_id": file_id,
          "owner_name": owner_name,
          "data_file": data_file,
          "cipher_aes": cipher_aes,
          "tag": tag,
          "session_key": session_key,
          "ts": _timestamp(ts),
          "last_updated": _timestamp(ts),
          "file_title": file_title,
          "file_for": file_for,
        },
      )
    return "okay"
  except Exception as exc:
    return exc
  finally:
    con.close()


@time_stuff
def updateFile(
  file_id,
  owner_name,
  data_file,
  tag,
  cipher_aes,
  session_key,
  last_updated,
  file_title,
  file_for,
):
  con = _connect()
  try:
    with con:
      cur = con.execute(
        """
        UPDATE lockedfiles
        SET data_file = :data_file,
            tag = :tag,
            cipher_aes = :cipher_aes,
            session_key = :session_key,
            last_updated = :last_updated,
            file_title = :file_title,
            file_for = :file_for
        WHERE file_id = :file_id AND owner_name = :owner_name
        """,
        {
          "data_file": data_file,
          "tag": tag,
          "cipher_aes": cipher_aes,
          "session_key": session_key,
          "last_updated": _timestamp(last_updated),
          "file_id": file_id,
          "owner_name": owner_name,
          "file_title": file_title,
          "file_for": file_for,
        },
      )
    return "okay" if cur.rowcount == 1 else "not_found"
  except Exception as exc:
    return exc
  finally:
    con.close()


@time_stuff
def retrieveFiles(session_uname):
  con = _connect()
  try:
    return con.execute(
      "SELECT * FROM lockedfiles WHERE owner_name = :session_uname",
      {"session_uname": session_uname},
    ).fetchall()
  finally:
    con.close()


@time_stuff
def retrieveSingleFile(file_id, owner_name):
  con = _connect(named_rows=True)
  try:
    return con.execute(
      """
      SELECT * FROM lockedfiles
      WHERE file_id = :file_id AND owner_name = :owner_name
      """,
      {"file_id": file_id, "owner_name": owner_name},
    ).fetchone()
  finally:
    con.close()


@time_stuff
def deleteFile(file_id, owner_name):
  con = _connect()
  try:
    with con:
      cur = con.execute(
        """
        DELETE FROM lockedfiles
        WHERE file_id = :file_id AND owner_name = :owner_name
        """,
        {"file_id": file_id, "owner_name": owner_name},
      )
    return "okay" if cur.rowcount == 1 else "not_found"
  except Exception as exc:
    return exc
  finally:
    con.close()


def upgrade_legacy_account(user_id, owner_name, password_hash, migrated_files):
  """Atomically migrate legacy documents and the password signature."""
  con = _connect()
  try:
    with con:
      for item in migrated_files:
        cur = con.execute(
          """
          UPDATE lockedfiles
          SET data_file = :data_file,
              cipher_aes = :cipher_aes,
              tag = :tag,
              session_key = :session_key,
              last_updated = :last_updated
          WHERE file_id = :file_id AND owner_name = :owner_name
          """,
          {**item, "owner_name": owner_name},
        )
        if cur.rowcount != 1:
          raise RuntimeError("A legacy document changed during migration")
      cur = con.execute(
        """
        UPDATE users
        SET password = :password, last_updated = :last_updated
        WHERE user_id = :user_id
        """,
        {
          "password": password_hash,
          "last_updated": datetime.now().isoformat(),
          "user_id": user_id,
        },
      )
      if cur.rowcount != 1:
        raise RuntimeError("User disappeared during migration")

      remaining_keys = con.execute("SELECT session_key FROM lockedfiles").fetchall()
      if all(
        isinstance(row[0], bytes) and row[0].startswith(b"v2:")
        for row in remaining_keys
      ):
        con.execute("DELETE FROM keys")
    return "success"
  except Exception as exc:
    return exc
  finally:
    con.close()


@time_stuff
def generate_keys():
  """Generate legacy keys only for compatibility with pre-v2 vaults."""
  from Crypto.Cipher import PKCS1_OAEP
  from Crypto.PublicKey import RSA
  from Crypto.Random import get_random_bytes

  con = _connect()
  try:
    key = RSA.generate(2048)
    public_bytes = key.publickey().export_key()
    private_bytes = key.export_key()
    session_key = get_random_bytes(16)
    enc_session_key = PKCS1_OAEP.new(RSA.import_key(public_bytes)).encrypt(session_key)
    with con:
      con.execute(
        "INSERT INTO keys(key_id, key_data, session_key) VALUES(?, ?, ?)",
        (b"public_key", public_bytes, session_key),
      )
      con.execute(
        "INSERT INTO keys(key_id, key_data, session_key) VALUES(?, ?, ?)",
        (b"private_key", private_bytes, enc_session_key),
      )
    return "An RSA Public Key was generated."
  except Exception as exc:
    return exc
  finally:
    con.close()


@time_stuff
def check_key(key_id):
  con = _connect(named_rows=True)
  try:
    return con.execute(
      "SELECT * FROM keys WHERE key_id = :key_id",
      {"key_id": key_id},
    ).fetchone()
  except Exception as exc:
    return exc
  finally:
    con.close()
