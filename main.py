#! /usr/bin/python3.11

# # # # #
# Installed Modules
# # # # #
import tkinter as tk
from tkinter.ttk import Frame, Button, Label, Notebook, Entry, Checkbutton
from datetime import timedelta, datetime
import secrets
from tkinter.messagebox import showinfo, showerror, askokcancel, askyesno
from tkinter.scrolledtext import ScrolledText

# # # #
# Local folders Modules
# # # #
from line_numbers import TextLineNumbers
from side_panel import SidePanel
from label_frame import LicencesFrame, Copyright
from styles import Stylings
from progress import Progress_Frame
from clock_frame import ClockFrame
#from libraries import missing_libs
import requirements

# Your original imports follow safely below:

ERROR = 'Error.TLabel'
SUCCESS = 'Success.TLabel'
WARNING = 'Warning.TLabel'
f = ('Times', 14)

def welcome_frame(root):
  root.geometry('256x298')

  welcome_fr = Frame(root)

  notebook = Notebook(welcome_fr, style="Notebook.TNotebook")
  notebook.pack(fill='both', pady=2, padx=2, expand=1)
  sign_in_tab(notebook, root)
  sign_up_tab(notebook, root)

  return welcome_fr
  
def sign_in_tab(notebook, root):
  # lazy import to avoid circular imports and unnecessary DB connections at startup
  from models import searchUser, insertCookie

  from generate_secrets import hashed_id, verify

  # function to get user data for confirmation
  def getIn(event=None):
    uname = email_tf.get().encode('utf-8')
    pwd = pwd_tf.get().encode('utf-8')

    expire_d = timedelta(minutes=2)
    expt = datetime.now() + expire_d

    if uname != ''.encode('utf-8') and pwd != ''.encode('utf-8'):
      user = searchUser(uname)

      if user != "ERROR" and user is not None and verify(cookie=user.user_name, sig=user.password, secret=pwd) == True:
        insertCookie(
          cookie_id=hashed_id(secrets.token_bytes(24)), cookie_owner_id = user.user_id, cookie_owner_username = user.user_name, ts = datetime.now(), cookie_owner_ts = user.ts, cookie_expire_time = expt.isoformat(), cookie_owner_last_updated=user.last_updated
        )
        email_tf.delete(0, 'end')
        pwd_tf.delete(0, 'end')
        root.destroy()
        create_main_app()
      else:
        showerror(title=
                  'Login Status', message='Invalid username or password')
    else:
      showerror(title='Oh!', message='Blank Form!')

  root.title('Welcome!')
  signin_frame = Frame(notebook, style="Notebook.TFrame", padding=16)
  Label(signin_frame, text="Username:", style="NotebookLabel.TLabel" ).grid(row=0, column=0, sticky='w', pady=(16, 0))

  Label(
      signin_frame, 
      text="Password:", style="NotebookLabel.TLabel" 
      ).grid(row=2, column=0, sticky='w', pady=(16, 0))
  email_tf = Entry(
      signin_frame, 
      font=f
      )
  email_tf.focus()
  email_tf.grid(row=1, column=0)
  pwd_tf = Entry(
      signin_frame,
      font=f,
      show='*'
      )
  pwd_tf.grid(row=3, column=0)
  login_btn = Button(
      signin_frame,
      text='Login',
      command=getIn,
      style='Signup.TButton',
      )
  login_btn.grid(row=4, column=0, pady=(32,8), sticky='w')
  login_btn.bind("<Return>", getIn)

  signin_frame.pack(fill='both', expand=1)
  notebook.add(signin_frame, text="User, sign in")

def sign_up_tab(notebook, root):
  # lazy import to avoid circular imports and unnecessary DB connections at startup
  from models import insertUser, logout_func
  from generate_secrets import hash_sign, hashed_id

  # Sign Up Function to connect to DB
  pwd_label = tk.StringVar()
  confirm_pwd_label = tk.StringVar()
  terms_var = tk.BooleanVar(value=False)

  def set_message(message, type=None):
    message_label['text'] = message
    if type:
      message_label['style'] = type

  def validate(*args):
    password = pwd_label.get()
    confirm_password = confirm_pwd_label.get()
    if confirm_password == password:
      set_message('Match!', SUCCESS)
      signup_btn['state'] = 'normal'
      return
    if password.startswith(confirm_password):
      set_message('Incomplete!', WARNING)
      return
    set_message("Passwords \nno match!", ERROR)
    signup_btn['state'] = 'disabled'

  def save():
    uname = email_tf.get().encode('utf-8')
    secret = pwd_tf.get().encode('utf-8')
    upwd = hash_sign(cookie=uname, secret=secret)

    if uname != ''.encode('utf-8') and secret != ''.encode('utf-8'):
      if terms_var.get() != False:
        mode = insertUser(user_id=hashed_id(secrets.token_bytes(24)), username=uname, password=upwd, timestamp=datetime.now())
        if mode == 'success':
          email_tf.delete(0, 'end')
          pwd_tf.delete(0, 'end')
          cpwd_tf.delete(0, 'end')
          showinfo('', 'Successfully saved account.')
          notebook.select(0)
        else:
          showerror('', "Username is taken. Please choose another one.")
      else:
        showerror('', 'Accept the terms to proceed.')
    else:
      showerror('', 'Blank form!')

  confirm_pwd_label.trace_add('write', validate)

  signup_frame = Frame(notebook, style="Notebook.TFrame", padding=16)

  Label(signup_frame, text="Username:", style="NotebookLabel.TLabel" ).grid(row=0, column=0, pady=(1, 0), sticky='w')
  email_tf = Entry(
    signup_frame, 
    font=f
    )
  email_tf.grid(row=1, column=0, sticky='w', pady=(0,5))

  Label(
    signup_frame, 
    text="Password:", style="NotebookLabel.TLabel"
    ).grid(row=2, column=0, pady=0, sticky='w')
  pwd_tf = Entry(
    signup_frame,
    font=f,
    show='*',
    textvariable=pwd_label
    )
  pwd_tf.grid(row=3, column=0, sticky='w', pady=(0,5))

  password_label_frame = Frame(signup_frame, style="Notebook.TFrame")
  password_label_frame.grid(row=4, column=0, sticky='w', pady=(5,0))

  Label(
    password_label_frame, 
    text="Confirm Password:", style="NotebookLabel.TLabel"
    ).grid(row=0, column=0, pady=0, padx=0, sticky='w')
  message_label = Label(
    password_label_frame,
    style='Success.TLabel'
    )
  message_label.grid(row=0, column=1, pady=0, padx=0, sticky='w')
  cpwd_tf = Entry(
    signup_frame,
    font=f,
    show='*',
    textvariable=confirm_pwd_label
    )
  cpwd_tf.grid(row=5, column=0, sticky='w', pady=0)

  terms_frame = Frame(signup_frame, style="Notebook.TFrame")
  terms_frame.grid(row=6, column=0, sticky='w', pady=(8,4))
  Checkbutton(terms_frame, text='Accept terms found here:', variable=terms_var, style="NotebookCheckbutton.TCheckbutton").grid(row=0, column=0, pady=0, padx=0, sticky='w')
  Button(terms_frame, text='terms', command=lambda: signup_frame.wait_window(Copyright(root).top)).grid(row=1, column=0, pady=0, padx=16, sticky='w')

  signup_btn = Button(
    signup_frame,
    text='Sign up',
    style='Signup.TButton',
    command=save
    )
  signup_btn['state'] = 'disabled'
  signup_btn.grid(row=7, column=0, pady=(12,0), sticky='w')
  signup_frame.pack(fill='both', expand=True)
  notebook.add(signup_frame, text="New user, sign up")

### Opening Frame
def base_frame_tab(root, session_cookie):
  # lazy import to avoid circular imports and unnecessary DB connections at startup
  from models import deleteFile, logout_func
  from extras.encryt import lock_file, decrypt
  from files_list import file_list
  
  root.geometry('976x512')
  def update_title():
    tit_time = datetime.fromisoformat(session_cookie.cookie_expire_time)
    return tit_time.strftime('%d/%m/%Y %X')
  
  root.title(f"This session is for {session_cookie.cookie_owner_username.decode('utf-8').capitalize()}. Expires at - {update_title()}")
  upd_id = tk.StringVar()

  base_frame = Frame(root, width=976, height=512)
  base_frame.columnconfigure(0, weight=1)

  text_scroll = ScrolledText(base_frame, padx=5, pady=4, wrap='word', relief='groove', background='#f3ba6c2f4', foreground='#eee2e8')

  line_number = TextLineNumbers(base_frame, width=30, relief='groove', bg='#6d2bc4')
  line_number.attach(text_scroll)
  line_number.pack(side='left', fill='y')

  def _on_change(event):
    return line_number.redraw()
  
  text_scroll.bind("<<Change>>", _on_change)
  text_scroll.bind("<Configure>", _on_change)
  text_scroll.event_generate("<<Paste>>")
  text_scroll.event_generate("<<Copy>>")
  text_scroll.event_generate("<<Cut>>")
  text_scroll.event_generate("<<Redo>>")
  text_scroll.event_generate("<<Undo>>")

  side_pane = SidePanel(base_frame, width=50, relief='raised')
  side_pane.attach(text_scroll)
  side_pane.pack(side='right', fill='y')
  
  def file_locker():
    lockm = lock_file(session_cookie, upd_id=None, text_message=text_scroll.get(1.0, 'end'), mode='create')
    if lockm != 'okay':
      showerror('', lockm)
      text_scroll.focus()
    else:
      new_doc()
      showinfo('', 'New document was stored!')

  def open_file_selector():
    pop_up = file_list(base_frame)
    base_frame.wait_window(pop_up.note)
    docid = pop_up.doc_id
    delid = pop_up.deleted_id
    upd_id.set(docid.get())

    if len(delid.get()) > 1:
      my_del = askokcancel('Delete file', f'Deleting : {delid.get()}.\nIrreversible action.\n\n\t\tDo you want to continue?')
      if my_del:
        deleted = deleteFile(delid.get().encode('utf-8'))
        print('Action: ', deleted)
        delid.set('')
      my_delete()
    else:
      pass

    if len(docid.get()) > 1:
      message = decrypt(docid)
      text_scroll.delete(1.0, 'end')
      text_scroll.insert(1.0, message)
      lock_btn['state'] = 'disabled'
      savebtn['state'] = 'normal'
      docid.set('')
      text_scroll.focus()
    else:
      return 'break'

  def my_delete():
    open_file_selector()

  def file_update():
    lockm = lock_file(session_cookie, upd_id, text_message=text_scroll.get(1.0, 'end'), mode='update')
    if lockm != 'okay':
      showerror('', lockm)
      text_scroll.focus()
    else:
      showinfo('', 'Document updated successfully!')

  lock_btn = Button(side_pane, text="Lock file", command=file_locker)
  savebtn = Button(side_pane, text="Save file", command=file_update)

  def new_doc():
    upd_id.set('')
    text_scroll.delete(1.0, 'end')
    savebtn['state'] = 'disabled'
    lock_btn['state'] = 'normal'
    text_scroll.focus() 

  def logout(cookie):
    logout_func(cookie)
    root.destroy()
    create_main_app()

  # Time showing
  ClockFrame(side_pane)

  Button(side_pane, text="New file", style="Newfile.TButton", command=new_doc).grid(row=0, column=0, padx=5, pady=10)
  lock_btn.grid(row=1, column=0, padx=5, pady=10)
  savebtn['state'] = 'disabled'
  savebtn.grid(row=2, column=0, padx=5, pady=10)
  Button(side_pane, text='Open file', command=open_file_selector).grid(row=3, column=0, padx=5, pady=10)
  Button(side_pane, text="Logout", style="Lougout.TButton", command=lambda : logout(session_cookie[0])).grid(row=5, column=0, padx=5, pady=5)
  LicencesFrame(side_pane)

  text_scroll.pack(fill='both', expand=1)
  
  return base_frame

def Run_Cookie(root, cookie):
    # Lazy imports to keep startup snappy
    from models import logout_func
    from monitor_cookie import cookie_monitor

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
    elif time_remaining <= timedelta(minutes=1):
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

def run_dependency_check():
    """
    Launches the progress bar window. Returns True if we are safe to proceed
    to the main app, or False if the user closed/cancelled it.
    """
    installer_root = tk.Tk()
    
    # Initialize your refactored Progress_Frame
    app = Progress_Frame(installer_root)
    
    # If all modules are already installed, skip loading the GUI entirely
    if not app.missing_modules:
        installer_root.destroy()
        return True

    # Start the Tkinter loop just for the installer window
    installer_root.mainloop()
    
    # Once installer_root is destroyed, return whether the download succeeded/skipped
    return app.p_result.get()

# create_main_app is the main function that launches the actual application after dependencies are verified and the user logs in. It is called at the end of the __main__ block.
def create_main_app():
    from models import verifyCookie, logout_func
    session_cookie = verifyCookie()
    
    root = tk.Tk()
    root.title('Cryptor App')
    root.resizable(0, 0)
    
    # Initialize a variable on root to hold our after loop ID
    root.check_run_id = None 

    Stylings(root)

    try: 
        root.wm_iconbitmap("cryp.ico") 
    except: 
        pass

    def lgt():
        # 🛑 CANCEL THE LOOP HERE BEFORE DESTROYING THE WINDOW
        if root.check_run_id is not None:
            root.after_cancel(root.check_run_id)
            
        if session_cookie is not None:
            if askyesno('Exiting...', 'The programme is shutting down now. All unsaved data may be lost permanently. You will be logged out automatically. \n\nDo you wish to proceed?'):
                logout_func(session_cookie[0])
                root.destroy()
        else:
            root.destroy()

    def check_run():
        Run_Cookie(root, session_cookie)
        # Capture the ID of the next scheduled loop
        root.check_run_id = root.after(1000, check_run)

    root.columnconfigure(0, weight=1)
    root.protocol("WM_DELETE_WINDOW", lgt)

    if session_cookie is not None:
        # Start the loop and save its initial ID
        root.check_run_id = root.after(1000, check_run)
        base = base_frame_tab(root, session_cookie)
        base.pack(fill='both', expand=1)
    else:
        welcome = welcome_frame(root)
        welcome.pack(fill='both', expand=1)

    root.mainloop()

#### RUN THE __MAIN__ FUNCTION ####
if __name__ == "__main__":
    # 1. Run the visual dependency installer wrapper FIRST.
    # This uses only Tkinter and standard libraries, so it won't crash!
    proceed_to_app = run_dependency_check()
    
    # 2. Only open the main app if the dependency window closed successfully
    if proceed_to_app:
        # Move the sensitive imports INSIDE this block.
        # They will only execute AFTER pycryptodome is guaranteed to be installed!
        print("Dependencies verified. Loading database and encryption modules...")
        from extras.init_run import run_connection
        
        # Now it is safe to establish database connections
        run_connection()
        
        # Launch the main application
        create_main_app()
    else:
        print("Application startup aborted by user.")
