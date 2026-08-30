import tkinter as tk

class TextLineNumbers(tk.Canvas):
  def __init__(self, *args, **kwargs):
    tk.Canvas.__init__(self, *args, **kwargs)
    self.textwidget = None
    self._redraw_after_id = None

  def attach(self, text_widget):
    self.textwidget = text_widget

  def redraw(self, *args):
    try:
      if (
        not self.winfo_exists()
        or self.textwidget is None
        or not self.textwidget.winfo_exists()
      ):
        return

      self.delete("all")
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
      return

    # UI events can call redraw repeatedly. Keep exactly one refresh timer so
    # logout has only one callback to cancel instead of a growing timer pool.
    if self._redraw_after_id is None:
      self._redraw_after_id = self.after(30, self._scheduled_redraw)

  def _scheduled_redraw(self):
    self._redraw_after_id = None
    self.redraw()

  def stop_redraw(self):
    after_id = self._redraw_after_id
    self._redraw_after_id = None
    if after_id is not None:
      try:
        self.after_cancel(after_id)
      except tk.TclError:
        pass

  def destroy(self):
    self.stop_redraw()
    super().destroy()
