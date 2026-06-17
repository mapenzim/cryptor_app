import tkinter as tk
from tkinter import ttk

class CustomModals:
  @staticmethod
  def center_modal(parent, modal, width, height):
    """Utility function to perfectly center the modal over the main application canvas."""
    parent.update_idletasks()
    
    # Get parent window position and bounds
    p_width = parent.winfo_width()
    p_height = parent.winfo_height()
    p_x = parent.winfo_x()
    p_y = parent.winfo_y()
    
    # Calculate target centered coordinates
    x = p_x + (p_width // 2) - (width // 2)
    y = p_y + (p_height // 2) - (height // 2)
    
    modal.geometry(f"{width}x{height}+{x}+{y}")

  @classmethod
  def ask_ok_cancel(cls, parent, title, message):
    """
    Custom replacement for askokcancel dialog box.
    Returns True if OK is pressed, False if Cancel or closed.
    """
    modal = tk.Toplevel(parent)
    modal.title(title)
    modal.configure(bg="#1e1e1e")
    modal.resizable(0, 0)
    
    # Force window focus and grab events (modal behavior)
    modal.transient(parent)
    modal.grab_set()
    
    cls.center_modal(parent, modal, width=420, height=180)
    
    result = {"value": False}
    
    def on_ok():
      result["value"] = True
      modal.destroy()
      
    def on_cancel():
      modal.destroy()

    # Layout Elements
    content_frame = ttk.Frame(modal, style="TFrame")
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Message Body
    msg_label = ttk.Label(
      content_frame, 
      text=message, 
      wraplength=380, 
      justify="center",
      font=("Helvetica", 10)
    )
    msg_label.pack(fill="both", expand=True, pady=(0, 15))
    
    # Actions Button Row Panel
    btn_frame = ttk.Frame(content_frame, style="TFrame")
    btn_frame.pack(fill="x", side="bottom")
    
    cancel_btn = ttk.Button(btn_frame, text="Cancel", command=on_cancel, style="Secondary.TButton")
    cancel_btn.pack(side="right", padx=(10, 0))
    
    ok_btn = ttk.Button(btn_frame, text="OK", command=on_ok, style="Accent.TButton")
    ok_btn.pack(side="right")
    
    # Wait for window to close before returning the dictionary reference state execution
    parent.wait_window(modal)
    return result["value"]

  @classmethod
  def show_error(cls, parent, title, message):
    """Custom replacement for showerror dialog box."""
    modal = tk.Toplevel(parent)
    modal.title(title)
    modal.configure(bg="#1e1e1e")
    modal.resizable(0, 0)
    
    modal.transient(parent)
    modal.grab_set()
    
    cls.center_modal(parent, modal, width=420, height=180)
    
    def on_close():
      modal.destroy()

    content_frame = ttk.Frame(modal, style="TFrame")
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Error Context Title Header Indicator
    error_header = ttk.Label(
      content_frame,
      text="⚠️ CRITICAL ERROR",
      font=("Helvetica", 11, "bold"),
      foreground="#ff5555" # Destructive Crimson red warning text mapping
    )
    error_header.pack(anchor="w", pady=(0, 5))
    
    msg_label = ttk.Label(
      content_frame, 
      text=message, 
      wraplength=380, 
      justify="left",
      font=("Helvetica", 10)
    )
    msg_label.pack(fill="both", expand=True, pady=(0, 15))
    
    btn_frame = ttk.Frame(content_frame, style="TFrame")
    btn_frame.pack(fill="x", side="bottom")
    
    close_btn = ttk.Button(btn_frame, text="Dismiss", command=on_close, style="Secondary.TButton")
    close_btn.pack(side="right")
    
    parent.wait_window(modal)