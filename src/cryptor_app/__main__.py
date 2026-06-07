import sys
from cryptor_app.main import create_main_app

def main():
  print("Initializing secure Cryptor Workspace canvas environment...")
  try:
    # 🚀 Fire your primary application entry pipeline directly
    create_main_app()
  except Exception as e:
    print(f"CRITICAL: System initialization loop aborted.\nDetails: {e}", file=sys.stderr)

if __name__ == "__main__":
  main()