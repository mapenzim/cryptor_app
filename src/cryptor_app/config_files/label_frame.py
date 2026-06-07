import tkinter as tk
from tkinter.ttk import *
import time

class LicencesFrame(LabelFrame):
  def __init__(self, master):
    # Explicitly configure LabelFrame style properties to match dark themes
    super().__init__(master, text='Licences')

    # Create two side-by-side buttons instead of vertical stacking to save vertical space in the sidebar
    self.columnconfigure(0, weight=1)
    self.columnconfigure(1, weight=1)
  
    # We pass self.master (the top-level window/root) down to the popups so they position correctly
    Button(
      self, 
      text='Licence', 
      style="Signup.TButton", 
      command=lambda: self.wait_window(LicenceDetails(self.winfo_toplevel()).top), 
      cursor='hand2'
    ).grid(row=0, column=0, padx=5, pady=8, sticky='ew')
    
    Button(
      self, 
      text='Copyright', 
      style="Signup.TButton", 
      command=lambda: self.wait_window(Copyright(self.winfo_toplevel()).top), 
      cursor='hand2'
    ).grid(row=0, column=1, padx=5, pady=8, sticky='ew')

class LicenceDetails(Frame):
  def __init__(self, master=None):
    super().__init__(master)
    
    self.top = tk.Toplevel(master, relief='flat')
    self.top.geometry("340x260")
    self.top.resizable(0,0)
    self.top.title('Licence Agreement')
    self.top.attributes('-topmost', True)
    self.top.configure(bg="#1e1e1e")

    # The icon 
    try: 
      self.top.wm_iconbitmap("cryp.ico") 
    except: 
      pass

    # Dark mode flat text block configuration
    self.text_fr = tk.Text(
      self.top, 
      height=10, 
      relief='flat', 
      bg='#2d2d2d', 
      fg='#ffffff', 
      font=('Arial', 10),
      padx=10,
      pady=10,
      wrap='word'
    )
    self.text_fr.pack(fill='both', expand=True, side='top', padx=10, pady=10)
    
    licence_text = (
      "This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.\n\n"
      "This is free software, and you are welcome to redistribute it under certain conditions; "
      "type `show c' for details."
    )
    self.text_fr.insert(1.0, licence_text)
    self.text_fr['state'] = 'disabled'

    # Styled copyright indicator string label
    lbl = Label(self.top, background="#2d2d2b", text=f"© 2021 - {time.strftime('%Y')} by Mapenzi Mudimba", font=('Arial', 9))
    lbl.pack(side='bottom', pady=(0, 10))

class Copyright(Frame):
  def __init__(self, master=None):
    super().__init__(master)
    
    self.top = tk.Toplevel(master, relief='flat')
    self.top.geometry("360x280")
    self.top.resizable(0,0)
    self.top.title('Copyright Metadata')
    self.top.attributes('-topmost', True)
    self.top.configure(bg="#1e1e1e")

    # The icon 
    try: 
      self.top.wm_iconbitmap("cryp.ico") 
    except: 
      pass

    # Container wrap panel
    self.frame_one = Frame(self.top, relief='flat')
    self.frame_one.pack(fill='both', expand=True, padx=10, pady=10)

    self.text_f = tk.Text(
      self.frame_one, 
      height=10, 
      relief='flat', 
      bg='#2d2d2d', 
      fg='#ffffff', 
      font=('Arial', 10),
      padx=10,
      pady=10,
      wrap='word'
    )
    self.text_f.pack(fill='both', expand=True)
    
    copyright_text = (
      "This page is licensed under the Python Software Foundation License Version 2.\n\n"
      "Examples, recipes, and other code in the documentation are additionally licensed "
      "under the Zero Clause BSD License.\n\n"
      "All rights reserved."
    )
    self.text_f.insert(1.0, copyright_text)
    self.text_f['state'] = 'disabled'
    
    lbl = Label(self.top, text=f"© 2021 - {time.strftime('%Y')} by Mapenzi Mudimba", font=('Arial', 9), background="#2d2d2b", foreground="#a89a76")
    lbl.pack(side='bottom', pady=(0, 10))