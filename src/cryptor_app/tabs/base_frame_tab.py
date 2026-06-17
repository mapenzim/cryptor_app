# # -------------------------------------------------- # #
# Installed Modules
# # -------------------------------------------------- # #
import os
import tkinter as tk
from tkinter.ttk import Frame, Button, Label
from datetime import datetime
from tkinter.scrolledtext import ScrolledText

# # --------------------------------------------------# #
# Local folders Modules
# # --------------------------------------------------# #
from cryptor_app.config_files.label_frame import LicencesFrame
from cryptor_app.config_files.line_numbers import TextLineNumbers
from cryptor_app.config_files.files_list import file_list
from cryptor_app.config_files.ai_texter import AITexterPanel
from cryptor_app.config_files.custom_modals import CustomModals

# _________________________________________________________
# Opening Frame
# -----------------------------------------------------------
def base_frame_tab(root, session_cookie, create_main_app):
  # ----------------------------------------------------
  # 🖥️ TASKBAR-AWARE FIXED MAXIMIZATION (LINUX / WINDOWS)
  # ----------------------------------------------------
  root.update_idletasks()
  root.state('normal')
  
  # Default fallback sizes
  custom_width = root.winfo_screenwidth()
  custom_height = root.winfo_screenheight() - 75
  start_x = 0
  start_y = 0

  # 🐧 Native Linux Check: Query the X11 usable workarea geometry bounds
  if os.name != 'nt':
    try:
      # Query the structural root window property manager for net workarea dimensions
      import subprocess
      output = subprocess.check_output("xprop -root _NET_WORKAREA", shell=True).decode()
      
      # xprop returns format: _NET_WORKAREA(CARDINAL) = x, y, width, height, ...
      if "=" in output:
        workarea_data = output.split("=")[1].strip().split(",")
        start_x = int(workarea_data[0].strip())
        start_y = int(workarea_data[1].strip())
        custom_width = int(workarea_data[2].strip())
        custom_height = int(workarea_data[3].strip())
    except Exception:
      # Fallback to standard offset math if xprop isn't present on the system
      start_x = 72 # Average width of the default Ubuntu Docker panel
      custom_width = root.winfo_screenwidth() - start_x
      custom_height = root.winfo_screenheight() - 75

  # 🚀 Apply the calculated offsets perfectly clearing the left docker edge
  root.geometry(f"{custom_width}x{custom_height}+{start_x}+{start_y}")
  root.update_idletasks()
  root.resizable(0, 0)
  
  upd_id = tk.StringVar()

  # Base container framework configuration
  base_frame = Frame(root, style="TFrame")
  base_frame.pack(fill='both', expand=True)
  root.configure(bg="#1e1e1e")

  # ----------------------------------------------------
  # 🟩 RIGHT COLUMN PANEL (Pre-initialized for binding)
  # ----------------------------------------------------
  editor_container = Frame(base_frame, relief='flat')

  text_scroll = ScrolledText(
    editor_container, 
    padx=10, 
    pady=10, 
    wrap='word', 
    relief='flat', 
    background='#252526', 
    foreground='#ffffff',
    insertbackground='#ffffff', 
    font=('Consolas', 11)
  )

  line_number = TextLineNumbers(editor_container, width=35, relief='flat', bg="#273e46")
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
  text_scroll.pack(side='left', fill='both', expand=True)

  # ----------------------------------------------------
  # 🗲 LEFT SIDEBAR INPUT TRACKS
  # ----------------------------------------------------
  left_sidebar = Frame(base_frame, width=320, style="Sidebar.TFrame")

  action_panel = Frame(left_sidebar, relief='flat', padding=10)
  action_panel.columnconfigure(0, weight=1)

  for_var = tk.StringVar()

  title_panel = Frame(action_panel, relief='flat')

  Label(title_panel, text="Document Title", font=('Arial', 9, 'bold'), background="#161616", foreground="#948f8f").pack(side='top', anchor='w', pady=2)
  title_entry = tk.Text(title_panel, height=2, bg="#51a8b0", fg="#0c054d", insertbackground="#090530", relief="flat", font=('Arial', 9), wrap='word')
  title_entry.pack(fill='x', expand=True, padx=(0, 4))
  title_panel.grid(row=1, column=0, sticky='ew', pady=(0, 6))

  purpose_panel = Frame(action_panel, relief="flat")

  Label(purpose_panel, text="Purpose / For:", font=('Arial', 9, 'bold'), background="#161616", foreground="#948f8f").pack(side="left")
  for_entry = tk.Entry(purpose_panel, textvariable=for_var, bg="#51a8b0", fg="#0c054d", insertbackground="#090530", relief="flat")
  for_entry.pack(side="right", fill='x', expand=True, padx=(4,0))

  purpose_panel.grid(row=2, column=0, sticky='ew', pady=(2,10))

  # ----------------------------------------------------
  # 🗲 TOP HEADER BANNER
  # ----------------------------------------------------
  header_banner = Frame(base_frame, padding=(20, 12), style="Header.TFrame")
  header_banner.pack(side='top', fill='x')

  # Left: session name label
  owner_name = session_cookie[2].decode('utf-8').capitalize() if isinstance(session_cookie[2], bytes) else str(session_cookie[2]).capitalize()
  info_lbl = Label(header_banner, text=f"Hi, {owner_name}. Chat with AITexter >>", font=('Arial', 10, 'bold'), foreground="#aaaaaa", background="#111111")
  info_lbl.pack(side='left', anchor='w', padx=(0, 15))
  
  root.session_expire_time = datetime.fromisoformat(session_cookie.cookie_expire_time)
  root.session_owner = owner_name

  # Right: logout btn
  def logout(cookie):
    from cryptor_app.extras.models import logout_func
    if hasattr(root, "check_run_id") and root.check_run_id is not None:
      root.after_cancel(root.check_run_id)
      root.check_run_id = None
    logout_func(cookie)
    root.destroy()
    create_main_app()

  logout_btn = Button(header_banner, text="Logout", style="Lougout.TButton", command=lambda: logout(session_cookie[0]), cursor="hand2")
  logout_btn.pack(side='right', anchor='e', padx=(15, 0))

  # Center Section: AI Content panel
  ai_texter_bar = AITexterPanel(header_banner, text_scroll, title_entry, for_var, editor_container)
  ai_texter_bar.pack(side='left', fill='x', expand=True, padx=(4,10))

  # ----------------------------------------------------
  # 🗲 RENDER LOWER LAYOUT PANELS (Preserves packaging flow)
  # ----------------------------------------------------
  left_sidebar.pack(side='left', fill='y', padx=(10, 5), pady=10)
  left_sidebar.pack_propagate(False)

  file_list_container = Frame(left_sidebar, relief='flat')
  file_list_container.pack(side='top', fill='both', expand=True, padx=5, pady=5)
  sidebar_explorer = file_list(file_list_container)

  action_panel.pack(side='bottom', fill='x', padx=5, pady=5)
  editor_container.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

  # ----------------------------------------------------
  # ⚙️ SYSTEM FILE CALLBACK HANDLING
  # ----------------------------------------------------
  def auto_load_file(event=None):
    from cryptor_app.extras.encryt import decrypt
    widget = sidebar_explorer.lst_files
    selected_item = widget.focus()
    if not selected_item: return

    current_selection = widget.item(selected_item, 'text')
    if not current_selection: return

    upd_id.set(current_selection)
    sidebar_explorer.doc_id.set(current_selection)

    tree_vals = widget.item(selected_item, 'values')
    if tree_vals:
      title_entry.delete("1.0", "end")
      title_entry.insert("1.0", tree_vals[0])
      for_var.set(tree_vals[1])

    try:
      message = decrypt(upd_id)
      text_scroll.delete(1.0, 'end')
      text_scroll.insert(1.0, message)
      lock_btn['state'] = 'disabled'
      lock_btn['cursor'] = 'circle'
      savebtn['state'] = 'normal'
      savebtn['cursor'] = 'hand2'
      text_scroll.focus()
    except Exception as err:
      CustomModals.show_error(root, "Decryption Failure", f"Could not read encrypted data block:\n{str(err)}")

  sidebar_explorer.lst_files.bind('<<TreeviewSelect>>', auto_load_file)

  def file_delete_handler():
    current_selection = sidebar_explorer.doc_id.get()
    if not current_selection:
      CustomModals.show_error(root, "Selection Error", "Please select a file from the list first.")
      return
    
    display_title = title_entry.get("1.0", "end-1c").strip()
    target_name = display_title if display_title else current_selection
    
    my_del = CustomModals.ask_ok_cancel(
      parent=root,
      title="Delete File",
      message=f"Permanently deleting: {target_name}\nThis operation removes data completely from database nodes. Proceed?"
    )
    if my_del:
      from cryptor_app.extras.models import deleteFile
      deleteFile(current_selection.encode('utf-8'))
      if upd_id.get() == current_selection: new_doc()
      else: sidebar_explorer.doc_id.set('')
      sidebar_explorer.refresh_list()
      CustomModals.show_error(root, "Success", "File record permanently wiped from storage nodes.")

  def file_locker():
    from cryptor_app.extras.encryt import lock_file
    t_str, f_str = title_entry.get("1.0", "end-1c").strip(), for_var.get().strip()
    if not t_str or not f_str:
      CustomModals.show_error(root, 'Input Missing', 'Please provide both a Document Title and a Purpose before locking.')
      return
    content = text_scroll.get(1.0, 'end-1c')
    lockm = lock_file(session_cookie, upd_id=None, text_message=content, mode='create', file_title=t_str, file_for=f_str)
    if lockm != 'okay': 
      CustomModals.show_error(root, 'Error', str(lockm))
      text_scroll.focus()
    else: 
      sidebar_explorer.refresh_list()
      new_doc()
      CustomModals.show_error(root, 'Success', 'New document safely encrypted and stored under Copyleft isolation parameters.')

  def file_update():
    from cryptor_app.extras.encryt import lock_file
    t_str, f_str = title_entry.get("1.0", "end-1c").strip(), for_var.get().strip()
    if not t_str or not f_str:
      CustomModals.show_error(root, 'Input Missing', 'Document Title and Purpose headers cannot be empty.')
      return
    content = text_scroll.get(1.0, 'end-1c')
    lockm = lock_file(session_cookie, upd_id, text_message=content, mode='update', file_title=t_str, file_for=f_str)
    if lockm != 'okay': 
      CustomModals.show_error(root, 'Error', str(lockm))
      text_scroll.focus()
    else: 
      sidebar_explorer.refresh_list()
      CustomModals.show_error(root, 'Success', 'Document transaction payload cipher addresses updated successfully!')

  def new_doc():
    upd_id.set('')
    sidebar_explorer.doc_id.set('')
    title_entry.delete(1.0, 'end')
    for_var.set('')
    text_scroll.delete(1.0, 'end')
    savebtn['state'] = 'disabled'
    savebtn['cursor'] = 'circle'
    lock_btn['state'] = 'normal'
    lock_btn['cursor'] = 'hand2'
    text_scroll.focus() 

  # ----------------------------------------------------
  # 🛠️ COMPONENT LAYOUT ASSEMBLY (BLUE ACTION PANEL)
  # ----------------------------------------------------
  lock_btn = Button(action_panel, text="Lock File (Create)", style="Signup.TButton", command=file_locker, cursor='hand2')
  savebtn = Button(action_panel, text="Save File (Update)", style="Signup.TButton", command=file_update, cursor="circle")
  savebtn['state'] = 'disabled'

  Button(action_panel, text="New File Workspace", style="Newfile.TButton", command=new_doc, cursor="hand2").grid(row=4, column=0, padx=2, pady=4, sticky='ew')
  lock_btn.grid(row=5, column=0, padx=2, pady=4, sticky='ew')
  savebtn.grid(row=6, column=0, padx=2, pady=4, sticky='ew')
  Button(action_panel, text="Delete Selected File", style="Delete.TButton", command=file_delete_handler, cursor="hand2").grid(row=7, column=0, padx=2, pady=4, sticky='ew')
  
  lic_box = LicencesFrame(action_panel)
  lic_box.grid(row=8, column=0, padx=2, pady=(12, 4), sticky='ew')
  
  return base_frame