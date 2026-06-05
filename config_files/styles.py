from tkinter.ttk import Style

def Stylings(root):
    style = Style(root)
    
    # 🛡️ Force 'clam' theme to unlock full background and hover color mappings
    if "clam" in style.theme_names():
        style.theme_use("clam")

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
        foreground='#ffffff',
        padding=(10, 6)
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
    style.configure("NotebookCheckbutton.TCheckbutton", relief="flat", background="#c08be7", foreground="white")