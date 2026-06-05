import tkinter as tk
from tkinter.ttk import *
from extras.models import retrieveFiles, verifyCookie
from datetime import datetime

lifont = ('Times', 12, 'italic')

class file_list(Frame):
    def __init__(self, master=None):
        # Initialize directly inside the master container provided (the top-left red zone)
        super().__init__(master)
        
        # 🛡️ Crucial Layout: Pack yourself inside the parent container to fill space completely
        self.pack(fill='both', expand=True)

        session_cookie = verifyCookie()
        self.all_files = retrieveFiles(session_cookie[2])
        
        # Public StringVars that base_frame_tab can read/trace at any time
        self.doc_id = tk.StringVar()
        self.deleted_id = tk.StringVar()

        # 🔴 Set up a simple descriptor label inside the sidebar workspace
        Label(self, text=f"Total Saved Files: {len(self.all_files)}", font=lifont, anchor='center', padding=4).pack(side='top', fill='x')

        # Main frame wrapper for Treeview list layout structures
        self.list_frame = Frame(self)
        self.list_frame.pack(fill='both', expand=True, padx=2, pady=2)

        # Build the dynamic list component tree
        self.lst_files = Treeview(self.list_frame, selectmode='browse')

        # Attach standard right-aligned scroll interface tracks
        self.lst_scrbar = Scrollbar(self.list_frame, command=self.lst_files.yview)
        self.lst_scrbar.pack(side='right', fill='y')
        self.lst_files['yscrollcommand'] = self.lst_scrbar.set

        # Strip down visible columns slightly to ensure it looks clean packed in a narrow sidebar width
        self.lst_files['columns'] = ('file_id', 'updated')

        # Formatting data widths for a compact sidebar layout configuration
        self.lst_files.column('#0', width=0, stretch='no')
        self.lst_files.column('file_id', width=160, anchor='w')
        self.lst_files.column('updated', width=100, anchor='center')

        # Format layout tracking column headers
        self.lst_files.heading('#0', text='', anchor='center')
        self.lst_files.heading('file_id', text='Document Name / ID', anchor='w')
        self.lst_files.heading('updated', text='Last Modified', anchor='center')

        # Populate the treeview table collection metrics
        count = 0
        for item in self.all_files:
            file_id_str = item[0].decode('utf-8') if isinstance(item[0], bytes) else str(item[0])
            
            # Grabbing the last updated ISO string cleanly
            try:
                mod_time = datetime.fromisoformat(item[7]).strftime('%d-%m-%Y %H:%M')
            except (ValueError, TypeError):
                mod_time = "Unknown"

            self.lst_files.insert(
                parent='', 
                index='end', 
                iid=count, 
                text='', 
                values=(file_id_str, mod_time)
            )
            count += 1

        # Bind native selection logic triggers
        self.lst_files.bind('<<TreeviewSelect>>', self.select_record)
        
        # Render out elements inside the list frame allocation zone
        self.lst_files.pack(fill='both', expand=True)

    def select_record(self, event):
        """ Fires automatically whenever an item inside the file explorer sidebar is highlighted """
        widget = event.widget
        selected_item = widget.focus()

        if selected_item:
            values = self.lst_files.item(selected_item, 'values')
            if values:
                # Silently updates the active document ID state variable.
                # Your main app loop or buttons can observe this value tracking update!
                self.doc_id.set(values[0])


    def refresh_list(self):
        """ Helper utility method to redraw the files tree after a record deletion or creation occurs """
        session_cookie = verifyCookie()
        self.all_files = retrieveFiles(session_cookie[2])
        
        # Drop all old data items out of view scope lists
        for item in self.lst_files.get_children():
            self.lst_files.delete(item)
            
        # Re-populate data entries smoothly
        count = 0
        for item in self.all_files:
            file_id_str = item[0].decode('utf-8') if isinstance(item[0], bytes) else str(item[0])
            try:
                mod_time = datetime.fromisoformat(item[7]).strftime('%d-%m-%Y %H:%M')
            except (ValueError, TypeError):
                mod_time = "Unknown"
                
            self.lst_files.insert(parent='', index='end', iid=count, text='', values=(file_id_str, mod_time))
            count += 1