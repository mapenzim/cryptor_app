import tkinter as tk
from tkinter.ttk import *

lifont = ('Times', 12, 'italic')

class cookie_monitor(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        # 🚚 LAZY IMPORT: Pull database tools safely right when the window initializes
        from extras.models import verifyCookie

        self.valueVar = tk.StringVar(value='no_action')
        self.session_cookie = verifyCookie()

        self.cookie_box = tk.Toplevel(master, relief='flat')
        self.cookie_box.geometry("360x120")
        self.cookie_box.attributes('-topmost', True)

        try:
            self.cookie_box.wm_iconbitmap("cryp.ico") 
        except: 
            pass
        
        username = self.session_cookie[2].decode('utf-8').capitalize()
        expire_time = self.session_cookie[4]
        self.cookie_id = self.session_cookie[0] 

        self.cookie_box.title(f'Session for {username}')

        Label(self.cookie_box, text=f"Session Cookie Expires at: {expire_time}", font=lifont, relief='ridge', padding=4).pack(side='top', fill='x')
        Label(self.cookie_box, text="Do you want to continue logged in?", font=lifont, relief='flat', padding=4).pack(fill='x')

        # BUTTON FRAME
        self.btns_frame = Frame(self.cookie_box, padding=(16,2))
        
        self.read_btn = Button(self.btns_frame, cursor='hand2', text="Yes, Continue", style='Decrypt.TButton', command=self.re_cookie)
        self.read_btn.grid(row=0, column=0, sticky=tk.W, padx=5)

        self.del_btn = Button(self.btns_frame, cursor='hand2', text="No, Logout", style='Delete.TButton', command=self.logout_user)
        self.del_btn.grid(row=0, column=1, sticky=tk.E, padx=5)

        self.btns_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.cookie_box.protocol("WM_DELETE_WINDOW", self.logout_user)
        self.cookie_box.focus()

    def re_cookie(self):
        # 🚚 LAZY IMPORT: Only imports when the user clicks 'Yes'
        from extras.models import renew_cookie
        from datetime import datetime, timedelta
        
        new_expiration = datetime.now() + timedelta(minutes=45)
        renew_cookie(cookie_id=self.cookie_id, cookie_expire_time=new_expiration.isoformat())
        
        self.valueVar.set('renewed')
        self.cookie_box.destroy()

    def logout_user(self):
        # 🚚 LAZY IMPORT: Only imports when the user clicks 'No' or closes the window
        from extras.models import logout_func
        
        logout_func(self.cookie_id)
        self.valueVar.set('logout')
        self.cookie_box.destroy()