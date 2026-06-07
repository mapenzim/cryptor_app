import tkinter as tk
from tkinter.ttk import *
from cryptor_app.extras.models import retrieveFiles, verifyCookie
from datetime import datetime

lifont = ('Times', 12, 'italic')

class file_list(Frame):
  def __init__(self, master=None):
    super().__init__(master)
    self.pack(fill='both', expand=True)

    session_cookie = verifyCookie()
    self.all_files = retrieveFiles(session_cookie[2])
    
    self.doc_id = tk.StringVar()
    self.deleted_id = tk.StringVar()

    Label(self, text=f"Total Saved Files: {len(self.all_files)}", font=lifont, anchor='center', padding=4).pack(side='top', fill='x')

    self.list_frame = Frame(self)
    self.list_frame.pack(fill='both', expand=True, padx=2, pady=2)

    self.lst_files = Treeview(self.list_frame, selectmode='browse')
    self.lst_scrbar = Scrollbar(self.list_frame, command=self.lst_files.yview)
    self.lst_scrbar.pack(side='right', fill='y')
    self.lst_files['yscrollcommand'] = self.lst_scrbar.set

    # Change columns to display Title and Purpose ("For")
    self.lst_files['columns'] = ('title', 'purpose')

    self.lst_files.column('#0', width=0, stretch='no')
    self.lst_files.column('title', width=130, anchor='w')
    self.lst_files.column('purpose', width=130, anchor='w')

    # Set readable column headers
    self.lst_files.heading('#0', text='', anchor='center')
    self.lst_files.heading('title', text='Title', anchor='w')
    self.lst_files.heading('purpose', text='Purpose / For', anchor='w')

    self.populate_tree()

    self.lst_files.bind('<<TreeviewSelect>>', self.select_record)
    self.lst_files.pack(fill='both', expand=True)

  def select_record(self, event):
    """ Fires automatically whenever an item inside the file explorer sidebar is highlighted """
    widget = event.widget
    selected_item = widget.focus()

    if selected_item:
      # 🛡️ FIX: Pull the actual file_id out of text, NOT the title values array
      file_id_str = widget.item(selected_item, 'text')
      if file_id_str:
        self.doc_id.set(file_id_str)

  def populate_tree(self):
    """ Sorts files chronologically and builds the visible treeview entries """
    
    # ⏱️ Sort files dynamically: Latest updated entries bubble directly to the top
    try:
      # item[7] is our last_updated ISO string timestamp from your database schema
      sorted_files = sorted(
        self.all_files, 
        key=lambda x: datetime.fromisoformat(x[7]) if (len(x) > 7 and x[7]) else datetime.min, 
        reverse=True
      )
    except Exception:
      # Fallback to unsorted state if any database timestamps happen to be corrupted
      sorted_files = self.all_files

    count = 0
    for item in sorted_files:
      # item[0] = file_id, item[8] = file_title, item[9] = file_for
      file_id_str = item[0].decode('utf-8') if isinstance(item[0], bytes) else str(item[0])
      title_str = item[8] if (len(item) > 8 and item[8]) else "Untitled"
      for_str = item[9] if (len(item) > 9 and item[9]) else "General"
      
      # We store the underlying hard file_id inside the item tags or text value 
      # so auto_load_file can still capture it instantly behind the scenes!
      self.lst_files.insert(
        parent='', 
        index='end', 
        iid=count, 
        text=file_id_str, # Secretly store the file_id here 
        values=(title_str, for_str)
      )
      count += 1

  def refresh_list(self):
    session_cookie = verifyCookie()
    self.all_files = retrieveFiles(session_cookie[2])
    for item in self.lst_files.get_children():
      self.lst_files.delete(item)
    self.populate_tree()