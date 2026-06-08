import tkinter as tk
from tkinter.ttk import *
from datetime import datetime, timedelta

class cookie_monitor(Frame):
  def __init__(self, master=None):
    super().__init__(master)
    self.pack()

    from cryptor_app.extras.models import verifyCookie

    self.root_window = master 
    self.session_cookie = verifyCookie()

    self.cookie_box = tk.Toplevel(master, relief='flat', bg="#1e1e1e")
    self.cookie_box.geometry("400x160")
    self.cookie_box.attributes('-topmost', True)
    self.cookie_box.resizable(0, 0)

    # 🖥️ Center the modal alert box relative to the primary monitor workspace bounds
    screen_w = self.cookie_box.winfo_screenwidth()
    screen_h = self.cookie_box.winfo_screenheight()
    pos_x = (screen_w // 2) - 200
    pos_y = (screen_h // 3) - 80
    self.cookie_box.geometry(f"400x160+{pos_x}+{pos_y}")

    try:
      self.cookie_box.wm_iconbitmap("cryp.ico") 
    except: 
      pass
    
    username = self.session_cookie[2].decode('utf-8').capitalize() if isinstance(self.session_cookie[2], bytes) else str(self.session_cookie[2]).capitalize()
    
    # Format raw expiration string cleanly for user readability
    try:
      raw_time = datetime.fromisoformat(self.session_cookie[4])
      expire_time = raw_time.strftime('%I:%M:%S %p')
    except Exception:
      expire_time = str(self.session_cookie[4])

    self.cookie_id = self.session_cookie[0] 
    self.cookie_box.title("Security Session Check")

    # Top Status Accent Header Panel
    top_banner = Frame(self.cookie_box, style="Header.TFrame", padding=(12, 10))
    top_banner.pack(side='top', fill='x')

    # Security Alert Text Configurations
    Label(
      top_banner, 
      text="⚠️  SESSION EXPIRATION WARNING", 
      font=('Arial', 10, 'bold'), 
      foreground="#ff5252", 
      background="#111111"
    ).pack(anchor='w')

    # Middle Content Body Container
    body_frame = Frame(self.cookie_box, style="TFrame", padding=(16, 12))
    body_frame.pack(fill='both', expand=True)

    Label(
      body_frame, 
      text=f"Your active session token is scheduled to expire at: {expire_time}", 
      font=('Arial', 9, 'bold'), 
      foreground="#aaaaaa", 
      background="#1e1e1e"
    ).pack(anchor='w', pady=(0, 4))

    Label(
      body_frame, 
      text="Would you like to extend your session credentials or log out?", 
      font=('Arial', 9), 
      foreground="#ffffff", 
      background="#1e1e1e"
    ).pack(anchor='w')

    # Bottom Interaction Button Container Row
    self.btns_frame = Frame(self.cookie_box, padding=(16, 12), style="TFrame")
    self.btns_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    self.btns_frame.columnconfigure(0, weight=1)
    self.btns_frame.columnconfigure(1, weight=1)

    self.read_btn = Button(
      self.btns_frame, 
      cursor='hand2', 
      text="Keep Me Logged In", 
      style='Signup.TButton', 
      command=self.re_cookie
    )
    self.read_btn.grid(row=0, column=0, sticky=tk.W, padx=(0, 6))

    self.del_btn = Button(
      self.btns_frame, 
      cursor='hand2', 
      text="Log Out Now", 
      style='Delete.TButton', 
      command=self.logout_user
    )
    self.del_btn.grid(row=0, column=1, sticky=tk.E, padx=(6, 0))

    self.cookie_box.protocol("WM_DELETE_WINDOW", self.logout_user)
    self.cookie_box.focus()

  def re_cookie(self):
    from extras.models import renew_cookie
    
    if hasattr(self.root_window, "check_run_id") and self.root_window.check_run_id is not None:
      self.root_window.after_cancel(self.root_window.check_run_id)
      self.root_window.check_run_id = None

    new_expiration = datetime.now() + timedelta(minutes=45)
    renew_cookie(cookie_id=self.cookie_id, cookie_expire_time=new_expiration.isoformat())
    
    self.root_window.monitor_active = False
    self.root_window.active_cookie_popup = None

    self.cookie_box.destroy()
    self.root_window.destroy()
    
    # 🚀 FIX: Import directly from the absolute package module path
    from cryptor_app.main import create_main_app
    create_main_app()
  
  def logout_user(self):
    ''' 
        ------- Ignore the Warning By Closing the popup -------------
        ------- The countdown continues in the background ---------- 
      '''
    self.root_window.active_cookie_popup = None
    self.cookie_box.destroy()

  '''
  def logout_user(self):
    #from cryptor_app.extras.models import logout_func
    
    #if hasattr(self.root_window, "check_run_id") and self.root_window.check_run_id is not None:
    #  self.root_window.after_cancel(self.root_window.check_run_id)
    #  self.root_window.check_run_id = None

    #logout_func(self.cookie_id)
    
    #self.root_window.monitor_active = False

    # ------- Ignore the Warning By Closing the popup -------------
    # ------- The countdown continues in the background ----------
    self.root_window.active_cookie_popup = None

    self.cookie_box.destroy()
    #self.root_window.destroy()
    
    #from __main__ import create_main_app
    #create_main_app()
  '''
