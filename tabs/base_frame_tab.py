# # # # #
# Installed Modules
# # # # #
import tkinter as tk
from tkinter.ttk import Frame, Button
from datetime import datetime
from tkinter.messagebox import showinfo, showerror, askokcancel
from tkinter.scrolledtext import ScrolledText

# # # #
# Local folders Modules (These do NOT import pycryptodome globally, so they are safe here!)
# # # #
from config_files.clock_frame import ClockFrame
from config_files.label_frame import LicencesFrame
from config_files.line_numbers import TextLineNumbers
from config_files.side_panel import SidePanel
from extras.models import logout_func, deleteFile
from config_files.files_list import file_list

### Opening Frame
def base_frame_tab(root, session_cookie, create_main_app):
  root.geometry('1314x704')
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
    # 🚚 LAZY IMPORT: Pull encryption logic only when a user actively clicks 'Lock file'
    from extras.encryt import lock_file

    lockm = lock_file(session_cookie, upd_id=None, text_message=text_scroll.get(1.0, 'end'), mode='create')
    if lockm != 'okay':
      showerror('', lockm)
      text_scroll.focus()
    else:
      new_doc()
      showinfo('', 'New document was stored!')

  def open_file_selector():
    # 🚚 LAZY IMPORT: Pull decryption logic only when reading an encrypted record
    from extras.encryt import decrypt

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
      lock_btn['cursor'] = 'circle'
      savebtn['state'] = 'normal'
      savebtn['cursor'] = 'hand2'
      docid.set('')
      text_scroll.focus()
    else:
      return 'break'

  def my_delete():
    open_file_selector()

  def file_update():
    # 🚚 LAZY IMPORT: Safely delay compilation link
    from extras.encryt import lock_file

    lockm = lock_file(session_cookie, upd_id, text_message=text_scroll.get(1.0, 'end'), mode='update')
    if lockm != 'okay':
      showerror('', lockm)
      text_scroll.focus()
    else:
      showinfo('', 'Document updated successfully!')

  lock_btn = Button(side_pane, text="Lock file", command=file_locker, cursor='hand2')
  savebtn = Button(side_pane, text="Save file", command=file_update, cursor="circle")

  def new_doc():
    upd_id.set('')
    text_scroll.delete(1.0, 'end')
    savebtn['state'] = 'disabled'
    savebtn['cursor'] = 'circle'
    lock_btn['state'] = 'normal'
    lock_btn['cursor'] = 'hand2'
    text_scroll.focus() 

  def logout(cookie):
    logout_func(cookie)
    root.destroy()
    create_main_app()

  # Time showing
  ClockFrame(side_pane)

  Button(
    side_pane, text="New file", style="Newfile.TButton", command=new_doc, cursor="hand2"
  ).grid(row=0, column=0, padx=5, pady=10)
  lock_btn.grid(row=1, column=0, padx=5, pady=10)
  savebtn['state'] = 'disabled'
  savebtn.grid(row=2, column=0, padx=5, pady=10)
  Button(
    side_pane, text='Open file', command=open_file_selector, cursor="hand2"
  ).grid(row=3, column=0, padx=5, pady=10)
  Button(
    side_pane, text="Logout", style="Lougout.TButton", command=lambda : logout(session_cookie[0]), cursor="hand2"
  ).grid(row=5, column=0, padx=5, pady=5)
  LicencesFrame(side_pane)

  text_scroll.pack(fill='both', expand=1)
  
  return base_frame