import tkinter as tk

class TextLineNumbers(tk.Canvas):
  def __init__(self, *args, **kwargs):
    tk.Canvas.__init__(self, *args, **kwargs)
    self.textwidget = None

  def attach(self, text_widget):
    self.textwidget = text_widget

  def redraw(self, *args):
    # 🛡️ Enhanced Safety check: Stop if canvas OR the attached text box is missing
    if not self.winfo_exists() or self.textwidget is None or not self.textwidget.winfo_exists():
      return
    
    '''redraw line numbers'''
    self.delete("all")

    try:
      i = self.textwidget.index("@0,0")
      while True :
        dline = self.textwidget.dlineinfo(i)
        if dline is None: 
          break
        y = dline[1]
        linenum = str(i).split(".")[0]
        self.create_text(2, y, anchor="nw", text=linenum, fill='#ff1')
        i = self.textwidget.index("%s+1line" % i)
    except tk.TclError:
      # Catch-all container in case a redraw fires mid-destruction
      return

    # Refreshes the canvas widget 30fps
    self.after(30, self.redraw)