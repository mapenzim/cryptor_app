import secrets
from tkinter.messagebox import askokcancel, showerror
from tkinter.ttk import Frame, Button, Label, Entry
from datetime import timedelta, datetime

from config_files.alert import alert_poper

f = ('Times', 14)

def sign_in_tab(notebook, root, create_main_app):
    # function to get user data for confirmation
    def getIn(event=None):
        # 🚚 LAZY IMPORTS: Safely contained inside the operational block.
        # These only execute AFTER the progress bar ensures they are fully installed.
        from extras.generate_secrets import hashed_id, verify
        from extras.models import insertCookie, searchUser

        uname = email_tf.get().encode('utf-8')
        pwd = pwd_tf.get().encode('utf-8')

        expire_d = timedelta(minutes=35)
        expt = datetime.now() + expire_d

        if uname != ''.encode('utf-8') and pwd != ''.encode('utf-8'):
            user = searchUser(uname)

            if user is None:
                oka = askokcancel("", "User not created")
                if oka:
                    notebook.select(1)
            else:
                if user != "ERROR" and verify(cookie=user.user_name, sig=user.password, secret=pwd) == True:
                    insertCookie(
                        cookie_id=hashed_id(secrets.token_bytes(24)), 
                        cookie_owner_id=user.user_id, 
                        cookie_owner_username=user.user_name, 
                        ts=datetime.now(), 
                        cookie_owner_ts=user.ts, 
                        cookie_expire_time=expt.isoformat(), 
                        cookie_owner_last_updated=user.last_updated
                    )
                    email_tf.delete(0, 'end')
                    pwd_tf.delete(0, 'end')
                    root.destroy()
                    create_main_app()
                else:
                    showerror(title='Login Status', message='Invalid username or password')
        else:
            showerror(title='Form is blank!', message='Please type in your credentials!')

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
        cursor='hand2'
        )
    login_btn.grid(row=4, column=0, pady=(32,8), sticky='w')
    login_btn.bind("<Return>", getIn)

    signin_frame.pack(fill='both', expand=1)
    notebook.add(signin_frame, text="User, sign in")