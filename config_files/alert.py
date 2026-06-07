import tkinter as tk
from tkinter.ttk import Frame, Button, Label

class alert_poper(Frame):
  def __init__(self, master=None):
    super().__init__(master)

    self.stringMsg = tk.StringVar()
    self.selected_notebook = tk.StringVar()

    # 1. Initialize modern dark flat modal window dimensions
    self.pop = tk.Toplevel(master, relief="flat", takefocus=True, padx=12, pady=12)
    self.pop.attributes('-topmost', True)
    self.pop.resizable(0, 0)
    self.pop.title("System Alert")
    self.pop.configure(bg="#1e1e1e") # Dark fallback background color

    try:
      self.pop.wm_iconbitmap('cryp.ico')
    except:
      pass

    # 2. Apply theme label styling flags
    Label(
      self.pop, 
      text="Missing information from the database.", 
      font=('Arial', 10, 'bold'),
      foreground="#ffffff",
      background="#1e1e1e"
    ).pack(side='top', fill='both', pady=(4, 0))

    # Inner container layout wrap block
    self.main_frm = Frame(self.pop, padding=(4, 16), style="Header.TFrame")
    self.main_frm.pack(fill="both", side="bottom")

    # 3. Dynamic layout action button integration matching design theme configurations
    self.yes_btn = Button(
      self.main_frm, 
      text='Go to register', 
      style="Signup.TButton",
      command=lambda: self.setVal("True"),
      cursor="hand2"
    )
    self.yes_btn.pack(side="left", padx=(0, 4))

    self.no_btn = Button(
      self.main_frm, 
      text="Cancel", 
      style="Delete.TButton",
      command=lambda: self.pop.destroy(),
      cursor="hand2"
    )
    self.no_btn.pack(side="right", padx=(4, 0))

    self.pack()
  
  def setVal(self, val):
    """ Sets the control variables and dismisses the alert frame cleanly """
    self.selected_notebook.set(val)
    self.pop.destroy()
  
  def manageWindow(self, winvar):
    self.stringMsg.set(winvar)