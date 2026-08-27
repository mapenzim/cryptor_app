# # # # #
# Installed Modules
# # # # #
from tkinter.ttk import Frame, Notebook

# # # #
# Local folders Modules
# # # #
from cryptor_app.tabs.sign_in_tab import sign_in_tab
from cryptor_app.tabs.sign_up_tab import sign_up_tab

def welcome_frame(root, switch_session):
  root.geometry('256x332')

  welcome_fr = Frame(root)

  notebook = Notebook(welcome_fr, style="Notebook.TNotebook")
  notebook.pack(fill='both', pady=2, padx=2, expand=1)
  sign_in_tab(notebook, root, switch_session)
  sign_up_tab(notebook, root)

  return welcome_fr
