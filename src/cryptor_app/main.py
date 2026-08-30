#! /usr/bin/python3.14
import os
import sys

import tkinter as tk
from datetime import datetime

from cryptor_app.config_files.progress import Progress_Frame
from cryptor_app.config_files.styles import Stylings

# 🛡️ Calculate the absolute package installation folder location dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXIT_APPLICATION = object()

def cancel_pending_tk_callbacks(widget):
  """Stop Tcl timers while leaving command cleanup to widget destruction."""
  try:
    pending = widget.tk.splitlist(widget.tk.call("after", "info"))
  except (AttributeError, tk.TclError):
    return

  for after_id in pending:
    try:
      # Do not call widget.after_cancel here. The timer may belong to a child
      # widget, and that wrapper also deletes the child's Tcl command without
      # removing it from the child's cleanup list. Raw Tcl cancellation stops
      # execution while normal widget destruction deletes the command once.
      widget.tk.call("after", "cancel", after_id)
    except (AttributeError, tk.TclError):
      pass

def run_dependency_check():
  """ Launches standalone visual check step frames. Returns true on confirmation """
  installer_root = tk.Tk()
  app = Progress_Frame(installer_root)
  
  if not app.missing_modules:
    cancel_pending_tk_callbacks(installer_root)
    installer_root.destroy()
    return True

  installer_root.mainloop()
  return app.p_result.get()

def create_main_app(session_context=None):
  # The application runner initializes the database before constructing screens.
  from cryptor_app.extras.models import verifyCookie, logout_func
  from cryptor_app.app_files.run_cookie import Run_Cookie
  from cryptor_app.app_files.welcome import welcome_frame
  from cryptor_app.tabs.base_frame_tab import base_frame_tab

  session_cookie = None
  vault_key = None
  if session_context is not None:
    candidate = session_context.get("cookie")
    if candidate is not None:
      session_cookie = verifyCookie(candidate.cookie_id)
      vault_key = session_context.get("vault_key")
    if session_cookie is None or vault_key is None:
      session_context = None
      session_cookie = None
      vault_key = None

  root = tk.Tk()
  root.title('Cryptor App')
  root.resizable(0, 0)
  
  root.check_run_id = None 
  root.active_cookie_popup = None # Pointer handle holding popup elements
  root.monitor_active = False
  root.next_session = EXIT_APPLICATION

  Stylings(root)

  try: 
    icon_path = os.path.join(BASE_DIR, "cryp.ico")
    root.wm_iconbitmap(icon_path)
  except: 
    pass

  def switch_session(next_session):
    if root.check_run_id is not None:
      try:
        root.after_cancel(root.check_run_id)
      except Exception:
        pass
      root.check_run_id = None
    root.next_session = next_session
    cancel_pending_tk_callbacks(root)
    root.destroy()

  def logout_transaction():
    from cryptor_app.config_files.custom_modals import CustomModals

    if session_cookie is not None:
      proceed = CustomModals.ask_ok_cancel(
        parent=root,
        title="Exiting...",
        message="The application is shutting down now. All unsaved workspace changes may be lost permanently. You will be logged out automatically.\n\nDo you want to proceed?"
      )
      if proceed:
        logout_func(session_cookie[0])
        switch_session(EXIT_APPLICATION)
    else:
      switch_session(EXIT_APPLICATION)
  
  def check_run():
    from datetime import datetime
    
    try:
      if not root or not root.winfo_exists():
        return
    except Exception:
      return

    Run_Cookie(root, session_cookie, switch_session)
    
    try:
      if not root or not root.winfo_exists():
        return
    except Exception:
      return

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
        
        if hasattr(root, "countdown_label") and root.countdown_label.winfo_exists():
          root.countdown_label.config(
            text=f"Logged in as: {root.session_owner}  •  Session Time Remaining: [ {countdown_string} ]"
          )
        root.title(f"Cryptor Workspace - Time Remaining: {countdown_string}")
      else:
        root.title("Session expired! Terminating environment...")

    try:
      if root.winfo_exists() and session_cookie is not None:
        root.check_run_id = root.after(1000, check_run)
    except Exception:
      pass

  root.columnconfigure(0, weight=1)
  root.protocol("WM_DELETE_WINDOW", logout_transaction)

  if session_cookie is not None:
    owner_str = session_cookie[2].decode('utf-8').capitalize() if isinstance(session_cookie[2], bytes) else str(session_cookie[2]).capitalize()
    root.session_owner = owner_str
    root.session_expire_time = datetime.fromisoformat(session_cookie.cookie_expire_time)

    base = base_frame_tab(
      root,
      session_cookie,
      vault_key,
      switch_session,
    )
    base.pack(fill='both', expand=1)
    
    root.check_run_id = root.after(1000, check_run)
  else:
    welcome = welcome_frame(root, switch_session)
    welcome.pack(fill='both', expand=1)

  root.mainloop()
  return root.next_session


def run_application():
  """Run each screen transition sequentially, without nested Tk mainloops."""
  from cryptor_app.extras.init_run import run_connection
  from cryptor_app.extras.models import expire_all_cookies

  run_connection()
  expire_all_cookies()
  session_context = None
  while True:
    session_context = create_main_app(session_context)
    if session_context is EXIT_APPLICATION:
      return 0

if __name__ == "__main__":
  proceed_to_app = run_dependency_check()
  
  if proceed_to_app:
    print("Dependencies verified. Initializing secure application database engines...")
    raise SystemExit(run_application())
  else:
    print("Application startup terminated by user.")
