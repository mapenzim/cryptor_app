from datetime import datetime, timedelta

def Run_Cookie(root, cookie, create_main_app):
  # Lazy imports to keep startup snappy
  from extras.models import logout_func
  from config_files.monitor_cookie import cookie_monitor

  if cookie is None:
    print("Not logged in.")
    return

  # Initialize a tracking flag on root to prevent multiple monitor popups spawning at once
  if not hasattr(root, "monitor_active"):
    root.monitor_active = False

  expire_time = datetime.fromisoformat(cookie.cookie_expire_time)
  time_remaining = expire_time - datetime.now()

  # --- SCENARIO 1: Cookie has completely expired ---
  if time_remaining <= timedelta(seconds=0):
    print("Session expired! Logging out automatically...")
        
    # 1. Cleanly cancel our main app background loop so it stops firing
    if hasattr(root, "check_run_id") and root.check_run_id is not None:
      root.after_cancel(root.check_run_id)
      root.check_run_id = None
            
    # 2. Update the backend database session state
    logout_func(cookie[0])
        
    # 3. Destroy the current window framework completely
    root.destroy()
        
    # 4. Trigger the fresh main app sequence (safely outside the loop context)
    create_main_app()
    return

  # --- SCENARIO 2: Cookie expires soon (<= 3 minutes remaining) ---
  elif time_remaining <= timedelta(minutes=3):
    # 🛡️ Only open the warning dialog if one isn't already visible on screen!
    if not root.monitor_active:
      root.monitor_active = True
            
      print(f"Session expiring soon! {time_remaining.total_seconds():.0f}s left.")
      cookie_window = cookie_monitor(root)
            
      # This halts this loop's execution until the user interacts with the popup
      root.wait_window(cookie_window.cookie_box)
            
      cookie_value = cookie_window.valueVar
      root.monitor_active = False # Window closed, clear the layout flag

      # Cancel background loops right before shifting app states
      if hasattr(root, "check_run_id") and root.check_run_id is not None:
        root.after_cancel(root.check_run_id)
        root.check_run_id = None

      if cookie_value.get() == 'renewed':
        print("Session successfully renewed by user.")
        root.destroy()
        create_main_app()
      else:
        print("User declined renewal or closed warning. Logging out.")
        logout_func(cookie[0])
        root.destroy()
        create_main_app()
                
  # --- SCENARIO 3: Session is perfectly safe (> 3 minutes remaining) ---
  else:
    # Everything is fine. Safely pass and let the 1-second interval loop continue
    pass