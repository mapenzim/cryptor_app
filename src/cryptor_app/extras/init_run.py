import sqlite3
import os

def run_connection():
  # 📁 Path to your database file (Flawlessly translates to /home/username/.cryptor_app/... on Ubuntu)
  db_path = os.path.expanduser('~/.cryptor_app/notebookserver.db')
  
  # 🔍 Extract the directory path
  db_dir = os.path.dirname(db_path)
  
  # 🛡️ If the directory doesn't exist, create it cleanly!
  if not os.path.exists(db_dir):
    print(f"Directory '{db_dir}' missing. Creating directory...")
    os.makedirs(db_dir, exist_ok=True) 
  
  # Initialize the SQLite connection with standard declaration type parsers
  init_connection = sqlite3.connect(
    db_path, 
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
  )
  
  cur = init_connection.cursor()
  
  # 1. Initialize Tables (Using explicit uppercase types to prevent conversion failures)
  cur.executescript('''
    BEGIN;
    CREATE TABLE IF NOT EXISTS lockedfiles(
      file_id TEXT PRIMARY KEY UNIQUE,
      owner_name TEXT,
      data_file TEXT,
      cipher_aes TEXT,
      tag TEXT,
      session_key TEXT,
      ts TIMESTAMP,
      last_updated TIMESTAMP,
      file_title TEXT,
      file_for TEXT
    );
    CREATE TABLE IF NOT EXISTS users(
      user_id TEXT PRIMARY KEY UNIQUE,
      user_name TEXT UNIQUE,
      password TEXT,
      ts TIMESTAMP,
      last_updated TIMESTAMP,
      cookie BOOLEAN
    );
    CREATE TABLE IF NOT EXISTS cookies(
      cookie_id TEXT PRIMARY KEY UNIQUE, 
      cookie_owner_id TEXT, 
      cookie_owner_username TEXT, 
      ts TIMESTAMP, 
      cookie_expire_time TIMESTAMP,
      cookie_owner_ts TIMESTAMP,
      cookie_owner_last_updated TIMESTAMP,
      cookie_expired BOOLEAN
    );
    CREATE TABLE IF NOT EXISTS keys(
      key_id TEXT PRIMARY KEY UNIQUE,
      key_data TEXT,
      session_key TEXT
    );
    COMMIT;
  ''')

  # 2. Schema Migration Guard for existing databases
  cur.execute("PRAGMA table_info(lockedfiles)")
  columns = [col[1] for col in cur.fetchall()]

  # Dynamically inject the new metadata columns if they aren't detected in an older file tree
  if "file_title" not in columns:
    print("Migrating schema: Adding 'file_title' column to lockedfiles...")
    cur.execute("ALTER TABLE lockedfiles ADD COLUMN file_title TEXT DEFAULT 'Untitled'")

  if "file_for" not in columns:
    print("Migrating schema: Adding 'file_for' column to lockedfiles...")
    cur.execute("ALTER TABLE lockedfiles ADD COLUMN file_for TEXT DEFAULT 'General'")

  init_connection.commit()
  init_connection.close() 
  print("Database connection established, migrations verified, and schemas updated successfully.")