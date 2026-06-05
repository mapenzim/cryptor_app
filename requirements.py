"""
Requirements for cryptor_app

This module lists and automatically installs all external dependencies required for the application to run.
Standard library modules (tkinter, sqlite3, datetime, etc.) are built-in and don't need installation.
"""

import sys
import subprocess
from importlib.metadata import entry_points, version, PackageNotFoundError

# 1. Base external packages that the app CANNOT run without
REQUIRED_PACKAGES = {
  'pycryptodome': 'pycryptodome>=3.15.0',  # Dict format: {'import_name_or_key': 'pip_install_name'}
}

# 2. Optional plugin entry points (if your app dynamically loads extensions)
# If you don't have dynamic plugins yet, you can leave this empty!
REQUIRED_PLUGINS = {
  # 'plugin_name': 'pip_package_name'
}

# Standard library modules (tracked for documentation/reference)
BUILTIN_MODULES = {
  'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.scrolledtext',
  'datetime', 'secrets', 'sqlite3', 'subprocess', 'os', 'timeit',
  'collections', 'hashlib', 'hmac', 'sys', 'threading', 'time'
}

def check_and_install_dependencies():
  print("Checking application dependencies...")

  # --- Step A: Check & Install Base Packages ---
  for import_name, pip_name in REQUIRED_PACKAGES.items():
    try:
      # Check if the package is installed
      version(import_name)
      print(f"-> Package '{import_name}' is already installed. Passing...")
    except PackageNotFoundError:
      print(f"-> Package '{import_name}' NOT found. Installing '{pip_name}'...")
      try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        print(f"Successfully installed {pip_name}!")
      except subprocess.CalledProcessError as e:
        print(f"Failed to install {pip_name}. Error: {e}")

    # --- Step B: Check & Install Dynamic Plugins (Using modern importlib) ---
  if REQUIRED_PLUGINS:
    # Discover all currently installed plugins for your app's group
    # (Change "cryptor.plugins" to match whatever group name you register in setup.py)
    installed_plugins = entry_points(group="cryptor.plugins")
    installed_names = {plugin.name for plugin in installed_plugins}

    for plugin_name, pip_package_name in REQUIRED_PLUGINS.items():
      if plugin_name in installed_names:
        print(f"-> Plugin '{plugin_name}' is already installed. Passing...")
      else:
        print(f"-> Plugin '{plugin_name}' NOT found. Installing '{pip_package_name}'...")
        try:
          subprocess.check_call([sys.executable, "-m", "pip", "install", pip_package_name])
          print(f"Successfully installed {pip_package_name}!")
        except subprocess.CalledProcessError as e:
          print(f"Failed to install {pip_package_name}. Error: {e}")

if __name__ == '__main__':
  # Run the automated installer
  check_and_install_dependencies()

  print("\nBuilt-in modules (built into Python, no installation needed):")
  for module in sorted(BUILTIN_MODULES):
    print(f"  - {module}")
