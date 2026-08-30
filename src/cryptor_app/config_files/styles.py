from tkinter.ttk import Style
import platform

def Stylings(root):
  style = Style(root)
  
  # 🍏 Step 1: Force cross-platform theme engine instantly before processing configurations
  if platform.system() == "Darwin":
    style.theme_use("clam")

  # 🎨 Step 2: Manually override the absolute global root style canvas configuration rule
  style.configure(".", background="#1e1e1e", foreground="#ffffff")

  # Step 3: Explicitly bind backup color arrays to the root component level
  root.configure(bg="#1e1e1e")

  # Dynamic Hover & Press states for buttons
  style.map("Signup.TButton",
    foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
    background=[('pressed', '#276c6a'), ('active', '#3fa8a5')]
  )
  style.map("Delete.TButton",
    foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
    background=[('pressed', '#a81c1c'), ('active', '#da2319')]
  )
  style.map("Newfile.TButton",
    foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
    background=[('pressed', '#1e5a38'), ('active', '#2bc475')]
  )
  style.map("Lougout.TButton",
    foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
    background=[('pressed', '#cc6600'), ('active', '#ff8000')]
  )

  # Base Global Styles for standard elements
  style.configure("TButton",
    font=('Arial', 10, 'bold'),
    relief='flat',
    background="#4a266a",
    foreground="#ffffff",
    padding=(10, 6)
  )

  style.map(
    'TButton',
    foreground=[("pressed", "blue"), ("active", "green")],
    background=[("pressed", "white"), ("active", "blue")]
  )

  # Keep form text legible on every ttk theme. Without an explicit
  # fieldbackground, some platforms combine the global white foreground with
  # the theme's default white Entry background.
  style.configure("TEntry",
    fieldbackground="#2e2e2e",
    foreground="#ffffff",
    insertcolor="#ffffff",
    selectbackground="#3fa8a5",
    selectforeground="#ffffff",
    bordercolor="#5e5e5e",
    padding=(6, 5)
  )
  style.map("TEntry",
    fieldbackground=[
      ('disabled', '#252526'),
      ('readonly', '#252526'),
      ('focus', '#2e2e2e')
    ],
    foreground=[
      ('disabled', '#9a9a9a'),
      ('readonly', '#ffffff')
    ],
    bordercolor=[('focus', '#3fa8a5')]
  )
  
  # 🔴 Smooth Treeview Styling for the File List
  style.configure("Treeview",
    background="#2e2e2e",
    fieldbackground="#2e2e2e",
    foreground="#ffffff",
    rowheight=28,
    font=('Arial', 10)
  )
  style.configure("Treeview.Heading",
    background="#1e1e1e",
    foreground="#ffffff",
    font=('Arial', 10, 'bold'),
    relief='flat'
  )
  style.map("Treeview",
    background=[('selected', '#3fa8a5')],
    foreground=[('selected', '#ffffff')]
  )

  # 🟢 Custom Small Round AI button configuration rule
  style.configure("RoundAI.TButton",
    font=('Arial', 13, 'bold'),
    background="#3fa8a5",
    foreground="#ffffff",
    width=3,
    padding=(2, 2),
    relief="flat"
  )
  style.map("RoundAI.TButton",
    background=[('pressed', '#276c6a'), ('active', '#51bcba')],
    foreground=[('pressed', '#ffffff'), ('active', '#ffffff')]
  )

  # Label Styles
  style.configure("Success.TLabel", font="Verdana 8", foreground='#a7f182', background="#c08be7")
  style.configure("Error.TLabel", font="Verdana 8", foreground='#da2319', background="#c08be7")
  style.configure("Warning.TLabel", font="Verdana 8", foreground='#f1d982', background="#c08be7")
  style.configure('Clock.TLabel', background='black', foreground='red')
  
  # App Panels and Frames
  style.configure("TFrame", background="#1e1e1e")
  style.configure("Header.TFrame", background="#111111", relief="flat")
  style.configure("Sidebar.TFrame", background="#1a1a1a", relief="flat")
  style.configure("Notebook.TNotebook", relief="flat")
  style.configure("Notebook.TFrame", relief="flat", background="#c08be7")
  style.configure("NotebookLabel.TLabel", relief="flat", background="#c08be7", foreground="white")
  style.configure("NotebookCheckbutton.TCheckbutton", relief="flat", background="#c08be7", foreground="blue")
