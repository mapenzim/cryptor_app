# # # # #
# Installed Modules
# # # # #
import tkinter as tk
from tkinter.ttk import Frame, Button, Label
from datetime import datetime
from tkinter.messagebox import showinfo, showerror, askokcancel
from tkinter.scrolledtext import ScrolledText

# # # #
# Local folders Modules
# # # #
from config_files.label_frame import LicencesFrame
from config_files.line_numbers import TextLineNumbers
from config_files.files_list import file_list

### Opening Frame
def base_frame_tab(root, session_cookie, create_main_app):
    root.geometry('1314x704')
    root.configure(bg="#1e1e1e") # Clean background fallback matching our frame colors
    
    def update_title():
        tit_time = datetime.fromisoformat(session_cookie.cookie_expire_time)
        return tit_time.strftime('%d/%m/%Y %H:%M:%S')
    
    root.title(f"Cryptor Workspace - Expires at: {update_title()}")
    upd_id = tk.StringVar()

    # Base container framework configuration
    base_frame = Frame(root, style="TFrame")
    base_frame.pack(fill='both', expand=True)

    # ----------------------------------------------------
    # 🗲 TOP HEADER BANNER (Dark aesthetic layout block)
    # ----------------------------------------------------
    header_banner = Frame(base_frame, padding=(20, 10), style="Header.TFrame")
    header_banner.pack(side='top', fill='x')

    session_text = f"Logged in as: {session_cookie.cookie_owner_username.decode('utf-8').capitalize()}  •  Session Expiring: {update_title()}"
    info_lbl = Label(header_banner, text=session_text, font=('Arial', 10, 'bold'), foreground="#aaaaaa", background="#111111")
    info_lbl.pack(side='left', anchor='w')

    def logout(cookie):
        from extras.models import logout_func
        logout_func(cookie)
        root.destroy()
        create_main_app()

    logout_btn = Button(header_banner, text="Logout", style="Lougout.TButton", command=lambda: logout(session_cookie[0]), cursor="hand2")
    logout_btn.pack(side='right', anchor='e')

    # ----------------------------------------------------
    # 🗲 LEFT COLUMN PANEL (Static horizontal width container)
    # ----------------------------------------------------
    left_sidebar = Frame(base_frame, width=320, style="Sidebar.TFrame")
    left_sidebar.pack(side='left', fill='y', padx=(10, 5), pady=10)
    left_sidebar.pack_propagate(False)

    # 🔴 TOP LEFT: Embedded File Explorer list structure
    file_list_container = Frame(left_sidebar, relief='flat')
    file_list_container.pack(side='top', fill='both', expand=True, padx=5, pady=5)
    
    sidebar_explorer = file_list(file_list_container)

    # 🔵 BOTTOM LEFT: Interactive Action Stack Dashboard 
    action_panel = Frame(left_sidebar, relief='flat', padding=10)
    action_panel.pack(side='bottom', fill='x', padx=5, pady=5)
    action_panel.columnconfigure(0, weight=1) # Dynamic row width spreading

    # ----------------------------------------------------
    # 🟩 RIGHT COLUMN PANEL (Main editor canvas workspace)
    # ----------------------------------------------------
    editor_container = Frame(base_frame, relief='flat')
    editor_container.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

    # Sleek dark text palette configurations
    text_scroll = ScrolledText(
        editor_container, 
        padx=10, 
        pady=10, 
        wrap='word', 
        relief='flat', 
        background='#252526', 
        foreground='#ffffff',
        insertbackground='#ffffff', # White blinking text typing caret cursor
        font=('Consolas', 11)
    )

    line_number = TextLineNumbers(editor_container, width=35, relief='flat', bg='#1e1e1e')
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
    # ⚙️ SYSTEM ACTIONS & SELECTION CALLBACK HANDLING
    # ----------------------------------------------------
    def auto_load_file(event=None):
        """ Instantly fires, extracts, and decrypts data when an item is selected """
        from extras.encryt import decrypt

        # 1. Directly interrogate the active sidebar list treeview
        widget = sidebar_explorer.lst_files
        selected_item = widget.focus()
        
        if not selected_item:
            return

        values = widget.item(selected_item, 'values')
        if not values or not values[0]:
            return

        # 2. Extract the raw string ID name
        current_selection = values[0]

        # 3. Forcefully sync your global string tracking states
        upd_id.set(current_selection)
        sidebar_explorer.doc_id.set(current_selection)

        try:
            # 4. Pass the tracked object to your decryption algorithm
            message = decrypt(upd_id)
            
            # 5. Clear the editor box and safely output the decrypted text string
            text_scroll.delete(1.0, 'end')
            text_scroll.insert(1.0, message)
            
            # Update UI action button states smoothly
            lock_btn['state'] = 'disabled'
            lock_btn['cursor'] = 'circle'
            savebtn['state'] = 'normal'
            savebtn['cursor'] = 'hand2'
            text_scroll.focus()
            
        except Exception as err:
            showerror("Decryption Failure", f"Could not read the encrypted data block:\n{str(err)}")

    sidebar_explorer.lst_files.bind('<<TreeviewSelect>>', auto_load_file)

    def file_delete_handler():
        current_selection = sidebar_explorer.doc_id.get()
        if not current_selection:
            showerror("Selection Error", "Please select a file from the list to delete first.")
            return
            
        my_del = askokcancel('Delete file', f'Deleting: {current_selection}.\nThis action is permanent. Proceed?')
        if my_del:
            from extras.models import deleteFile
            deleteFile(current_selection.encode('utf-8'))
            
            if upd_id.get() == current_selection:
                new_doc()
            else:
                sidebar_explorer.doc_id.set('')
                
            sidebar_explorer.refresh_list()
            showinfo('Success', 'File removed successfully.')

    def file_locker():
        from extras.encryt import lock_file
        content = text_scroll.get(1.0, 'end-1c')
        lockm = lock_file(session_cookie, upd_id=None, text_message=content, mode='create')
        
        if lockm != 'okay':
            showerror('Error', str(lockm))
            text_scroll.focus()
        else:
            sidebar_explorer.refresh_list()
            new_doc()
            showinfo('Success', 'New document encrypted and stored!')

    def file_update():
        from extras.encryt import lock_file
        content = text_scroll.get(1.0, 'end-1c')
        lockm = lock_file(session_cookie, upd_id, text_message=content, mode='update')
        
        if lockm != 'okay':
            showerror('Error', str(lockm))
            text_scroll.focus()
        else:
            sidebar_explorer.refresh_list()
            showinfo('Success', 'Document updated successfully!')

    def new_doc():
        upd_id.set('')
        sidebar_explorer.doc_id.set('')
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

    # Clean action stacking matching our style scheme rules
    Button(action_panel, text="New File Workspace", style="Newfile.TButton", command=new_doc, cursor="hand2").grid(row=0, column=0, padx=2, pady=4, sticky='ew')
    lock_btn.grid(row=1, column=0, padx=2, pady=4, sticky='ew')
    savebtn.grid(row=2, column=0, padx=2, pady=4, sticky='ew')
    Button(action_panel, text="Delete Selected File", style="Delete.TButton", command=file_delete_handler, cursor="hand2").grid(row=3, column=0, padx=2, pady=4, sticky='ew')
    
    # ⚙️ INSTANTIATE AND PLACE THE REFRACTORED FRAME RIGHT HERE
    lic_box = LicencesFrame(action_panel)
    lic_box.grid(row=4, column=0, padx=2, pady=(12, 4), sticky='ew')
    
    return base_frame