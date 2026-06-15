#! /usr/bin/python3.14
import os
import sys

import tkinter as tk
from tkinter.messagebox import askyesno
from datetime import datetime

from cryptor_app.config_files.progress import Progress_Frame
from cryptor_app.config_files.styles import Stylings

# 🛡️ Calculate the absolute package installation folder location dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_dependency_check():
  """ Launches standalone visual check step frames. Returns true on confirmation """
  installer_root = tk.Tk()
  app = Progress_Frame(installer_root)
  
  if not app.missing_modules:
    installer_root.destroy()
    return True

  installer_root.mainloop()
  return app.p_result.get()


def create_main_app():
  from cryptor_app.extras.models import verifyCookie, logout_func
  from cryptor_app.app_files.run_cookie import Run_Cookie
  from cryptor_app.app_files.welcome import welcome_frame
  from cryptor_app.tabs.base_frame_tab import base_frame_tab

  session_cookie = verifyCookie()
  
  root = tk.Tk()
  root.title('Cryptor App')
  root.resizable(0, 0)
  
  root.check_run_id = None 
  root.active_cookie_popup = None # Pointer handle holding popup elements
  root.monitor_active = False

  Stylings(root)

  try: 
    icon_path = os.path.join(BASE_DIR, "cryp.ico")
    root.wm_iconbitmap(icon_path)
  except: 
    pass

  def logout_transaction():
    if root.check_run_id is not None:
      root.after_cancel(root.check_run_id)
      root.check_run_id = None

    if session_cookie is not None:
      if askyesno('Exiting...', 'The programme is shutting down now. All unsaved data may be lost permanently. You will be logged out automatically. \n\nDo you want to proceed?'):
        logout_func(session_cookie[0])
        root.destroy()
    else:
      root.destroy()
  
  def check_run():
    from datetime import datetime
    
    # 🛡️ THE CRUCIAL GUARD ROUTINE: Short-circuit immediately if the window has been shut down
    try:
      if not root or not root.winfo_exists():
        return
    except Exception:
      # If the Tcl engine is completely unmapped or dead, exit silently
      return

    # 1. Fire our dynamic, unblocked security state loop validation check
    Run_Cookie(root, session_cookie, create_main_app)
    
    # Double-check existence again after Run_Cookie processes just in case it triggered an auto-logout
    try:
      if not root or not root.winfo_exists():
        return
    except Exception:
      return

    # 2. Check if components have initialized inside the active runtime workspace
    if hasattr(root, "session_owner") and hasattr(root, "session_expire_time"):
      now = datetime.now()
      expiry = root.session_expire_time
      
      if expiry > now:
        time_diff = expiry - now
        total_seconds = int(time_diff.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        countdown_string = f"{hours:02d} hr : {minutes:02d} min : {seconds:02d} sec"
        
        # Safe string modification configuration
        if hasattr(root, "countdown_label") and root.countdown_label.winfo_exists():
          root.countdown_label.config(
            text=f"Logged in as: {root.session_owner}  •  Session Time Remaining: [ {countdown_string} ]"
          )
        root.title(f"Cryptor Workspace - Time Remaining: {countdown_string}")
      else:
        # Hard lock fallback execution if user didn't accept choices
        root.title("Session expired! Terminating environment...")

    # Continue the background loop heart beating every 1000ms
    try:
      if root.winfo_exists() and session_cookie is not None:
        root.check_run_id = root.after(1000, check_run)
    except Exception:
      pass

  root.columnconfigure(0, weight=1)
  root.protocol("WM_DELETE_WINDOW", logout_transaction)

  if session_cookie is not None:
    # Set base references early before thread loop spins up
    owner_str = session_cookie[2].decode('utf-8').capitalize() if isinstance(session_cookie[2], bytes) else str(session_cookie[2]).capitalize()
    root.session_owner = owner_str
    root.session_expire_time = datetime.fromisoformat(session_cookie.cookie_expire_time)

    base = base_frame_tab(root, session_cookie, create_main_app)
    base.pack(fill='both', expand=1)
    
    # Trigger background monitor checks loop execution
    root.check_run_id = root.after(1000, check_run)
  else:
    welcome = welcome_frame(root, create_main_app)
    welcome.pack(fill='both', expand=1)

  root.mainloop()


if __name__ == "__main__":
  proceed_to_app = run_dependency_check()
  
  if proceed_to_app:
    print("Dependencies verified. Initializing secure application database engines...")
    from cryptor_app.extras.init_run import run_connection
    run_connection()
    create_main_app()
  else:
    print("Application startup terminated by user.")