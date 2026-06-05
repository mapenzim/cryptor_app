import tkinter as tk
from tkinter.ttk import *

class alert_poper(Frame):
  def __init__(self, master=None):
    super().__init__(master)

    self.stringMsg = tk.StringVar()
    self.selected_notebook = tk.StringVar()

    self.pop = tk.Toplevel(master, relief="flat", takefocus=True, padx=8, pady=8)
    self.pop.attributes('-topmost', True)
    self.pop.resizable(0, 0)
    self.pop.title("Alert !!")

    try:
      self.pop.wm_iconbitmap('cryp.ico')
    except:
      pass

    Label(self.pop, text="Missing information fom the database").pack(side='top', fill='both')

    self.main_frm = Frame(self.pop, padding=(4,16))
    self.main_frm.pack(fill="both", side="bottom")

    self.yes_btn = Button(self.main_frm, text='Go to register', command=lambda: self.setVal("True"))
    self.yes_btn.pack(side="left")

    self.no_btn = Button(self.main_frm, text="Cancel", command=lambda: self.pop.destroy())
    self.no_btn.pack(side="right")

    self.pack();
  
  def setVal(self, val):
    self.selected_notebook.set(val)
    #self.pop.destroy()
  
  def manageWindow(self, winvar):
    self.stringMsg.set(winvar)
  