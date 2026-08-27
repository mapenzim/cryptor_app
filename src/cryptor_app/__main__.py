import sys


def _load_application():
  from cryptor_app.main import run_application
  return run_application

def main():
  print("Initializing secure Cryptor Workspace canvas environment...")
  try:
    return _load_application()()
  except Exception as e:
    print(f"CRITICAL: System initialization loop aborted.\nDetails: {e}", file=sys.stderr)
    return 1

if __name__ == "__main__":
  raise SystemExit(main())
