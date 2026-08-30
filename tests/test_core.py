import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timedelta
from hashlib import blake2b
from unittest.mock import Mock, patch

from Crypto.Cipher import AES

from cryptor_app.extras import models
from cryptor_app.extras.encryt import (
  KEY_FORMAT,
  decrypt,
  lock_file,
  prepare_legacy_migration,
)
from cryptor_app.extras.generate_secrets import (
  derive_vault_key,
  hash_sign,
  is_legacy_signature,
  verify,
)
from cryptor_app.extras.init_run import run_connection

try:
  import tkinter  # noqa: F401
  TKINTER_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
  TKINTER_AVAILABLE = False


class Value:
  def __init__(self, value):
    self.value = value

  def get(self):
    return self.value


class CoreTests(unittest.TestCase):
  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.home_patch = patch.dict(os.environ, {"HOME": self.temp_dir.name})
    self.home_patch.start()
    models.db_path = os.path.join(
      self.temp_dir.name,
      ".cryptor_app",
      "notebookserver.db",
    )
    run_connection()
    self.now = datetime.now()

  def tearDown(self):
    self.home_patch.stop()
    self.temp_dir.cleanup()

  def create_user_and_session(self, username=b"alice", password=None):
    password = password or (b"a" * 80)
    signature = hash_sign(username, password)
    vault_key = derive_vault_key(signature, password)
    user_id = b"user-" + username
    self.assertEqual(
      models.insertUser(user_id, username, signature, self.now),
      "success",
    )
    cookie = models.insertCookie(
      b"cookie-" + username,
      user_id,
      username,
      self.now,
      (self.now + timedelta(minutes=45)).isoformat(),
      self.now,
      self.now,
    )
    return signature, vault_key, cookie

  def test_long_password_and_wrong_password(self):
    password = b"p" * 80
    signature = hash_sign(b"alice", password)
    self.assertTrue(verify(b"alice", signature, password))
    self.assertFalse(verify(b"alice", signature, b"wrong password"))
    self.assertEqual(len(derive_vault_key(signature, password)), 32)

  def test_create_update_decrypt_and_owner_isolation(self):
    _, vault_key, cookie = self.create_user_and_session()
    self.assertEqual(
      lock_file(
        cookie,
        None,
        "first secure secret",
        "create",
        "Title",
        "Purpose",
        vault_key,
      ),
      "okay",
    )
    row = models.retrieveFiles(b"alice")[0]
    self.assertTrue(row[5].startswith(KEY_FORMAT))
    self.assertNotEqual(row[5], vault_key)
    file_id = row[0].decode("utf-8")
    self.assertEqual(decrypt(Value(file_id), cookie, vault_key), "first secure secret")

    self.assertEqual(
      lock_file(
        cookie,
        Value(file_id),
        "updated secure secret",
        "update",
        "New Title",
        "New Purpose",
        vault_key,
      ),
      "okay",
    )
    self.assertEqual(decrypt(Value(file_id), cookie, vault_key), "updated secure secret")
    with self.assertRaises(ValueError):
      decrypt(Value(file_id), cookie, b"x" * 32)
    self.assertIsNone(models.retrieveSingleFile(row[0], b"bob"))
    self.assertEqual(models.deleteFile(b"missing", b"alice"), "not_found")

  def test_cookie_selection_is_exact_single_and_unexpired(self):
    _, _, first = self.create_user_and_session()
    expired = models.insertCookie(
      b"expired",
      b"user-alice",
      b"alice",
      self.now,
      (self.now - timedelta(seconds=1)).isoformat(),
      self.now,
      self.now,
    )
    self.assertEqual(expired.cookie_id, b"expired")
    self.assertIsNone(models.verifyCookie(b"expired"))
    second = models.insertCookie(
      b"new",
      b"user-alice",
      b"alice",
      self.now + timedelta(seconds=1),
      (self.now + timedelta(minutes=5)).isoformat(),
      self.now,
      self.now,
    )
    self.assertEqual(models.verifyCookie().cookie_id, second.cookie_id)
    self.assertIsNone(models.verifyCookie(first.cookie_id))

  def test_legacy_account_and_documents_migrate_atomically(self):
    username = b"legacy"
    password = b"legacy password"
    legacy_hasher = blake2b(digest_size=32, key=password)
    legacy_hasher.update(username)
    legacy_signature = legacy_hasher.hexdigest().encode("ascii")
    self.assertEqual(
      models.insertUser(b"legacy-user", username, legacy_signature, self.now),
      "success",
    )

    legacy_key = b"L" * 16
    cipher = AES.new(legacy_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(b"legacy secret text")
    self.assertEqual(
      models.insertFile(
        b"legacy-file",
        username,
        ciphertext,
        cipher.nonce,
        tag,
        legacy_key,
        self.now,
        "Legacy",
        "Migration",
      ),
      "okay",
    )

    new_signature = hash_sign(username, password)
    vault_key = derive_vault_key(new_signature, password)
    migrated = prepare_legacy_migration(username, vault_key)
    self.assertEqual(len(migrated), 1)
    self.assertEqual(
      models.upgrade_legacy_account(
        b"legacy-user",
        username,
        new_signature,
        migrated,
      ),
      "success",
    )
    updated_user = models.searchUser(username)
    self.assertFalse(is_legacy_signature(updated_user.password))
    self.assertTrue(verify(username, updated_user.password, password))
    self.assertTrue(models.retrieveFiles(username)[0][5].startswith(KEY_FORMAT))

  def test_retrieve_users_uses_real_schema_column(self):
    self.create_user_and_session()
    users = models.retrieveUsers()
    self.assertEqual(users[0][0], b"alice")

  def test_startup_failure_returns_nonzero(self):
    from cryptor_app import __main__

    stderr = io.StringIO()
    with patch.object(__main__, "_load_application", side_effect=RuntimeError("boom")):
      with redirect_stderr(stderr):
        self.assertEqual(__main__.main(), 1)
    self.assertIn("boom", stderr.getvalue())

  @unittest.skipUnless(TKINTER_AVAILABLE, "Tkinter is not installed")
  def test_shutdown_cancels_all_pending_tk_callbacks(self):
    from cryptor_app.main import cancel_pending_tk_callbacks

    root = Mock()
    root.tk.call.return_value = ("after#1", "after#2")
    root.tk.splitlist.return_value = ("after#1", "after#2")

    cancel_pending_tk_callbacks(root)

    root.tk.call.assert_any_call("after", "cancel", "after#1")
    root.tk.call.assert_any_call("after", "cancel", "after#2")
    root.after_cancel.assert_not_called()

  @unittest.skipUnless(TKINTER_AVAILABLE, "Tkinter is not installed")
  def test_line_number_redraw_keeps_only_one_timer(self):
    from cryptor_app.config_files.line_numbers import TextLineNumbers

    canvas = object.__new__(TextLineNumbers)
    canvas.textwidget = Mock()
    canvas.textwidget.winfo_exists.return_value = True
    canvas.textwidget.index.side_effect = ["1.0", "2.0", "1.0", "2.0"]
    canvas.textwidget.dlineinfo.side_effect = [(0, 0), None, (0, 0), None]
    canvas._redraw_after_id = None

    with (
      patch.object(TextLineNumbers, "winfo_exists", return_value=True),
      patch.object(TextLineNumbers, "delete"),
      patch.object(TextLineNumbers, "create_text"),
      patch.object(TextLineNumbers, "after", return_value="after#1") as after,
    ):
      canvas.redraw()
      canvas.redraw()

    after.assert_called_once_with(30, canvas._scheduled_redraw)

  @unittest.skipUnless(TKINTER_AVAILABLE, "Tkinter is not installed")
  def test_entry_style_uses_contrasting_field_and_text_colors(self):
    from cryptor_app.config_files import styles

    root = Mock()
    style = Mock()
    with (
      patch.object(styles, "Style", return_value=style),
      patch.object(styles.platform, "system", return_value="Darwin"),
    ):
      styles.Stylings(root)

    entry_config = next(
      call.kwargs
      for call in style.configure.call_args_list
      if call.args == ("TEntry",)
    )
    self.assertNotEqual(
      entry_config["fieldbackground"],
      entry_config["foreground"],
    )
    self.assertEqual(entry_config["insertcolor"], entry_config["foreground"])
    style.map.assert_any_call(
      "TEntry",
      fieldbackground=[
        ('disabled', '#252526'),
        ('readonly', '#252526'),
        ('focus', '#2e2e2e'),
      ],
      foreground=[
        ('disabled', '#9a9a9a'),
        ('readonly', '#ffffff'),
      ],
      bordercolor=[('focus', '#3fa8a5')],
    )

  @unittest.skipUnless(TKINTER_AVAILABLE, "Tkinter is not installed")
  def test_success_modal_uses_success_status_instead_of_critical_error(self):
    from cryptor_app.config_files.custom_modals import CustomModals

    parent = Mock()
    with patch.object(CustomModals, "_show_message") as show_message:
      CustomModals.show_success(
        parent=parent,
        title="Success",
        message="Saved.",
      )

    show_message.assert_called_once_with(
      parent=parent,
      title="Success",
      message="Saved.",
      header="✅ SUCCESS",
      header_foreground="#7ddc83",
      message_foreground="#ffffff",
    )

  @unittest.skipUnless(TKINTER_AVAILABLE, "Tkinter is not installed")
  def test_missing_ollama_model_error_has_install_instructions(self):
    from cryptor_app.config_files.ai_texter import AITexterPanel

    message = AITexterPanel._friendly_worker_error(
      "Ollama API error 404: model 'llama3:8b' not found",
    )
    self.assertIn("ollama pull llama3:8b", message)
    self.assertIn("not installed", message)

  @unittest.skipUnless(TKINTER_AVAILABLE, "Tkinter is not installed")
  def test_ollama_timeout_error_is_actionable(self):
    from httpx import ReadTimeout
    from cryptor_app.config_files.ai_texter import AITexterPanel

    message = AITexterPanel._friendly_worker_error(ReadTimeout(""))
    self.assertIn("exceeded 300 seconds", message)
    self.assertIn("CRYPTOR_OLLAMA_TIMEOUT", message)

  @unittest.skipUnless(TKINTER_AVAILABLE, "Tkinter is not installed")
  def test_session_renewal_uses_absolute_import_and_updates_runtime(self):
    from cryptor_app.config_files.monitor_cookie import cookie_monitor

    _, _, cookie = self.create_user_and_session()
    monitor = object.__new__(cookie_monitor)
    monitor.root_window = Mock(check_run_id=None, monitor_active=True)
    monitor.root_window.active_cookie_popup = Mock()
    monitor.cookie_box = Mock()
    monitor.cookie_id = cookie.cookie_id
    monitor.re_cookie()
    self.assertFalse(monitor.root_window.monitor_active)
    self.assertIsNone(monitor.root_window.active_cookie_popup)
    self.assertIsInstance(monitor.root_window.session_expire_time, datetime)
    monitor.cookie_box.destroy.assert_called_once()


if __name__ == "__main__":
  unittest.main()
