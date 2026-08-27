import secrets
from tkinter.ttk import Frame, Button, Label, Entry
from datetime import timedelta, datetime

f = ('Times', 14)

def sign_in_tab(notebook, root, switch_session):

  # function to get user data for confirmation
  def getIn(event=None):
    # 🚚 LAZY IMPORTS: Safely contained inside the operational block.
    # These only execute AFTER the progress bar ensures they are fully installed.
    from cryptor_app.extras.generate_secrets import (
      derive_vault_key,
      hash_sign,
      hashed_id,
      is_legacy_signature,
      verify,
    )
    from cryptor_app.extras.models import (
      insertCookie,
      searchUser,
      upgrade_legacy_account,
    )
    from cryptor_app.extras.encryt import prepare_legacy_migration
    from cryptor_app.config_files.custom_modals import CustomModals

    uname = email_tf.get().strip().encode('utf-8')
    pwd = pwd_tf.get().encode('utf-8')

    expire_d = timedelta(minutes=45)
    expt = datetime.now() + expire_d

    if uname != ''.encode('utf-8') and pwd != ''.encode('utf-8'):
      user = searchUser(uname)

      if user is None:
        # 🚀 Custom dark-themed alert for missing workspace account profile
        oka = CustomModals.ask_ok_cancel(
          parent=root,
          title="Account Missing",
          message="User profile not found. Would you like to switch to the registration tab to create a new key account?"
        )
        if oka:
          notebook.select(1)
      elif user == "ERROR":
        CustomModals.show_error(
          parent=root,
          title="Database Error",
          message="The user database could not be read. No session was created."
        )
      else:
        if verify(cookie=user.user_name, sig=user.password, secret=pwd):
          try:
            password_signature = user.password
            if is_legacy_signature(password_signature):
              password_signature = hash_sign(cookie=user.user_name, secret=pwd)
              vault_key = derive_vault_key(password_signature, pwd)
              migrated_files = prepare_legacy_migration(user.user_name, vault_key)
              migration = upgrade_legacy_account(
                user.user_id,
                user.user_name,
                password_signature,
                migrated_files,
              )
              if migration != "success":
                raise RuntimeError(str(migration))
            else:
              vault_key = derive_vault_key(password_signature, pwd)
          except Exception as exc:
            CustomModals.show_error(
              parent=root,
              title="Vault Migration Failed",
              message=f"Your existing data was left unchanged.\n\n{exc}"
            )
            return

          session_cookie = insertCookie(
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
          switch_session({"cookie": session_cookie, "vault_key": vault_key})
        else:
          # 🚀 Custom error frame for failed signature verification matching
          CustomModals.show_error(
            parent=root,
            title="Login Status",
            message="Invalid username or master password string entry. Security token evaluation failed."
          )
    else:
      # 🚀 Custom error frame for layout input validation checks
      CustomModals.show_error(
        parent=root,
        title="Form is blank!",
        message="Please type in your security workspace credentials to clear the isolation vault!"
      )


  root.title('Welcome!')
  signin_frame = Frame(notebook, style="Notebook.TFrame", padding=16)
  
  Label(signin_frame, text="Username:", style="NotebookLabel.TLabel").grid(row=0, column=0, sticky='w', pady=(16, 0))

  email_tf = Entry(signin_frame, font=f)
  email_tf.focus()
  email_tf.grid(row=1, column=0, sticky='ew')

  Label(signin_frame, text="Password:", style="NotebookLabel.TLabel").grid(row=2, column=0, sticky='w', pady=(16, 0))
  
  pwd_tf = Entry(signin_frame, font=f, show='*')
  pwd_tf.grid(row=3, column=0, sticky='ew')
  
  login_btn = Button(
    signin_frame,
    text='Login',
    command=getIn,
    style='Signup.TButton',
    cursor='hand2'
  )
  login_btn.grid(row=4, column=0, pady=(32, 8), sticky='w')
  
  # Frame-wide return key binding to handle submissions gracefully
  root.bind("<Return>", getIn)

  signin_frame.pack(fill='both', expand=1)
  notebook.add(signin_frame, text="User, sign in")
