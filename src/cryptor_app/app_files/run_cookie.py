from datetime import datetime, timedelta

def Run_Cookie(root, cookie, create_main_app):
  # Lazy imports to keep startup snappy
  from cryptor_app.extras.models import logout_func
  from cryptor_app.config_files.monitor_cookie import cookie_monitor

  if cookie is None:
    print("Not logged in.")
    return

  if not hasattr(root, "monitor_active"):
    root.monitor_active = False

  expire_time = datetime.fromisoformat(cookie.cookie_expire_time)
  time_remaining = expire_time - datetime.now()

  # --- SCENARIO 1: Cookie has completely expired at 0 seconds ---
  if time_remaining <= timedelta(seconds=0):
    print("Session expired! Forcibly terminating environment...")
        
    # 🛡️ Dynamic Guard: Forcibly kill the lingering popup alert box if it's still open on screen
    if hasattr(root, "active_cookie_popup") and root.active_cookie_popup is not None:
      try:
        root.active_cookie_popup.destroy()
      except Exception:
        pass
      root.active_cookie_popup = None

    if hasattr(root, "check_run_id") and root.check_run_id is not None:
      root.after_cancel(root.check_run_id)
      root.check_run_id = None
            
    logout_func(cookie[0])
    root.destroy()
    create_main_app()
    return

  # --- SCENARIO 2: Cookie expires soon (<= 3 minutes remaining) ---
  elif time_remaining <= timedelta(minutes=3):
    # Only spawn a new window if one isn't currently alive
    if not root.monitor_active:
      root.monitor_active = True
      print(f"Session expiring soon! {time_remaining.total_seconds():.0f}s left.")
      
      # Instantiate the window panel
      cookie_window = cookie_monitor(root)
      
      # 🛡️ Keep a reference on root so our 1-second checker can access and destroy it at 0s
      root.active_cookie_popup = cookie_window.cookie_box
      
      # REMOVED: root.wait_window() - We allow the main thread loop to keep ticking!

  # --- SCENARIO 3: Session is perfectly safe (> 3 minutes remaining) ---
  else:
    root.monitor_active = False
    root.active_cookie_popup = None