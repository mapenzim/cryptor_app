import secrets
import tkinter as tk
from tkinter.messagebox import askokcancel, showerror, showinfo
from tkinter.ttk import Frame, Button, Label, Entry, Checkbutton
from datetime import datetime

from cryptor_app.config_files.label_frame import Copyright

ERROR = 'Error.TLabel'
SUCCESS = 'Success.TLabel'
WARNING = 'Warning.TLabel'
f = ('Times', 14)

def sign_up_tab(notebook, root):
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
      signup_btn['cursor'] = 'hand2'
      return
    if password.startswith(confirm_password):
      set_message('Incomplete!', WARNING)
      return
    set_message("Passwords \nno match!", ERROR)
    signup_btn['state'] = 'disabled'
    signup_btn['cursor'] = 'circle'

  def save():
    # 🚚 LAZY IMPORTS: Safely tucked away inside the click event.
    # These will only evaluate AFTER the progress bar window ensures they exist!
    from cryptor_app.extras.generate_secrets import hash_sign, hashed_id
    from cryptor_app.extras.models import insertUser

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
          ask = askokcancel("User exists", "This user is already registered. \nIf you are the owner of the username and forgot password, please reset your password. \nTo go back to login, please select 'OK' button below. \nIf you want to change the username, click 'Cancel' button to remain on this screen.")
          if ask:
            notebook.select(0)
      else:
        showerror('', 'Accept the terms to proceed.')
    else:
      showerror('', 'Blank form!')

  confirm_pwd_label.trace_add('write', validate)

  signup_frame = Frame(notebook, style="Notebook.TFrame", padding=16)

  Label(signup_frame, text="Username:", style="NotebookLabel.TLabel" ).grid(row=0, column=0, pady=(1, 0), sticky='w')
  email_tf = Entry(signup_frame, font=f)
  email_tf.grid(row=1, column=0, sticky='w', pady=(0,5))

  Label(signup_frame, text="Password:", style="NotebookLabel.TLabel").grid(row=2, column=0, pady=0, sticky='w')
  pwd_tf = Entry(signup_frame, font=f, show='*', textvariable=pwd_label)
  pwd_tf.grid(row=3, column=0, sticky='w', pady=(0,5))

  password_label_frame = Frame(signup_frame, style="Notebook.TFrame")
  password_label_frame.grid(row=4, column=0, sticky='w', pady=(5,0))

  Label(password_label_frame, text="Confirm Password:", style="NotebookLabel.TLabel").grid(row=0, column=0, pady=0, padx=0, sticky='w')
  message_label = Label(password_label_frame, style='Success.TLabel')
  message_label.grid(row=0, column=1, pady=0, padx=0, sticky='w')
  
  cpwd_tf = Entry(signup_frame, font=f, show='*', textvariable=confirm_pwd_label)
  cpwd_tf.grid(row=5, column=0, sticky='w', pady=0)

  terms_frame = Frame(signup_frame, style="Notebook.TFrame")
  terms_frame.grid(row=6, column=0, sticky='w', pady=(8,4))
  Checkbutton(terms_frame, text='Accept terms found here:', variable=terms_var, style="NotebookCheckbutton.TCheckbutton", cursor='hand2').grid(row=0, column=0, pady=0, padx=0, sticky='w')
  Button(terms_frame, text='terms', cursor='hand2', command=lambda: signup_frame.wait_window(Copyright(root).top)).grid(row=1, column=0, pady=0, padx=16, sticky='w')

  signup_btn = Button(
    signup_frame,
    text='Sign up',
    style='Signup.TButton',
    command=save,
    cursor="circle"
  )
  signup_btn['state'] = 'disabled'
  signup_btn.grid(row=7, column=0, pady=(12,0), sticky='w')
  signup_frame.pack(fill='both', expand=True)
  notebook.add(signup_frame, text="New user, sign up")
