import tkinter as tk
from tkinter.ttk import Frame, Button, Label, Combobox
from tkinter.messagebox import showerror, askokcancel
from datetime import datetime
import threading
import asyncio

class AITexterPanel(Frame):
  def __init__(self, master, text_scroll, title_entry, for_var, editor_container):
    super().__init__(master, style="Header.TFrame")
    
    self.text_scroll = text_scroll
    self.title_entry = title_entry
    self.for_var = for_var
    self.editor_container = editor_container

    # Context Preset Dropdown Setup
    self.preset_var = tk.StringVar(value="Generate Secure Password")
    self.ai_dropdown = Combobox(self, textvariable=self.preset_var, values=["Generate Secure Password", "Draft Cryptographic Note", "Custom Prompt..."], state="readonly", width=22)
    self.ai_dropdown.pack(side='left', padx=(0, 6), ipady=4)

    # Prompt Entry Field
    self.prompt_var = tk.StringVar(value="Create a unique 16-character complex password with symbols.")
    self.prompt_entry = tk.Entry(self, textvariable=self.prompt_var, bg="#23586E", fg="#ffffff", insertbackground="#64A424", relief="flat")
    self.prompt_entry.pack(side='left', fill='x', expand=True, padx=(2, 6), ipadx=4, ipady=4)

    self.ai_dropdown.bind("<<ComboboxSelected>>", self.handle_preset_change)

    # Action Button
    self.ai_btn = Button(
      self,  
      text="●",
      style="RoundAI.TButton",
      command=self.trigger_ai_generation, 
      cursor="hand2"
    )
    self.ai_btn.pack(side='left', padx=(2, 0))

    # Tracking state parameters for the animation engine loop
    self.is_generating = False
    self.blink_state = False
    self.overlay = None

  def handle_preset_change(self, event):
    choice = self.preset_var.get()
    if choice == "Generate Secure Password":
      self.prompt_var.set("Create a unique 16-character complex password with symbols.")
    elif choice == "Draft Cryptographic Note":
      self.prompt_var.set("Draft a secure template for storing multi-factor authentication backup keys.")
    elif choice == "Custom Prompt...":
      self.prompt_var.set("")
      self.prompt_entry.focus()

  def trigger_ai_generation(self):
    prompt_text = self.prompt_var.get().strip()
    if not prompt_text:
      showerror("Prompt Empty", "Please type an AI instruction or select a security preset first.")
      return

    # Smart Insertion Guard
    current_content = self.text_scroll.get(1.0, 'end-1c').strip()
    if current_content:
      confirm = askokcancel("Overwrite Warning", "The workspace contains active content. Generating fresh text will wipe the screen. Continue?")
      if not confirm:
        return

    # Engage generation flags to trigger the blinking loop sequence
    self.is_generating = True
    self.ai_btn.config(state="disabled")
    self.animate_blinking()
    self.winfo_toplevel().update_idletasks()

    # Instantiate and map our sleek loading overlay right over the editor frame zone!
    self.overlay = AILoadingOverlay(self.editor_container)

    # 🚀 FIX: Pass a synchronous runner method as the thread target to prevent window freezing
    worker = threading.Thread(target=self._thread_run_loop, args=(prompt_text,))
    worker.daemon = True
    worker.start()

  def _thread_run_loop(self, prompt_text):
    """ Secondary isolation bridge that safely initializes a fresh async loop inside the thread """
    asyncio.run(self.async_ai_worker(prompt_text))

  def animate_blinking(self):
    """ Continuous style-toggling function running on a background loop """
    if not self.winfo_exists() or not self.is_generating:
      return

    # Toggle between two visual style variations
    if self.blink_state:
      self.ai_btn.config(text="○", style="RoundAI.TButton")
    else:
      self.ai_btn.config(text="●", style="RoundAI.TButton")

    self.blink_state = not self.blink_state
        
    # Keep ticking every 200 milliseconds
    self.after(200, self.animate_blinking)

  async def async_ai_worker(self, prompt_text):
    try:
      import secrets, string
      from ollama import AsyncClient
      
      # Use non-blocking async sleep instead of time.sleep()
      await asyncio.sleep(1)

      client = AsyncClient()

      if "password" in prompt_text.lower():
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+"
        generated_result = "".join(secrets.choice(alphabet) for _ in range(16))
        generated_result = f"--- GENERATED SECURE CREDENTIAL ---\n\nPassword: {generated_result}\n\nGenerated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n[Keep this note encrypted for maximum safety]"
      else:
        response = await client.chat(
          model='llama3:8b',
          messages=[
            {
              'role': 'system',
              'content': 'You are a secure local cryptographic helper. Output requested text, credentials, or password data structures immediately. Do not introduce conversational chatter or say "Here is your output".'
            },
            {
              'role': 'user',
              'content': prompt_text
            }
          ]
        )
        generated_result = response['message']['content']

      # Route data output back to GUI loop safely
      self.winfo_toplevel().after(0, lambda: self.direct_ai_output_to_editor(generated_result))

    except Exception as e:
      self.winfo_toplevel().after(0, lambda: self.handle_worker_error(str(e)))

  def direct_ai_output_to_editor(self, result_text):
    self.is_generating = False
    
    if self.overlay:
      self.overlay.destroy()
      self.overlay = None

    self.text_scroll.delete(1.0, 'end')
    self.text_scroll.insert(1.0, result_text)
    
    if "Password" in result_text:
      self.title_entry.insert("1.0","Generated Access Token")
      self.for_var.set("Secure Credential Access Key")
    
    self.ai_btn.config(state="normal", text="●", style="RoundAI.TButton")
    self.text_scroll.focus()

  def handle_worker_error(self, error_message):
    self.is_generating = False
    if self.overlay:
      self.overlay.destroy()
      self.overlay = None
        
    showerror("AI API Error", f"Transaction failed:\n{error_message}")
    self.ai_btn.config(state="normal", text="●", style="RoundAI.TButton")


# ----------------------------------------------------
# 🛡️ SLEEK HIGH-REACTIVITY LOADING OVERLAY PANEL
# ----------------------------------------------------
class AILoadingOverlay(Frame):
  def __init__(self, master):
    super().__init__(master, relief="flat")
    
    self.place(relx=0, rely=0, relwidth=1, relheight=1)
    self.configure(style="Header.TFrame") 

    # Centered structural layout alignment holder
    center_box = Frame(self, style="Header.TFrame")
    center_box.place(relx=0, rely=0.45, relwidth=1, anchor="w")

    # 🔄 Native Vector Spinner Canvas Instance
    self.spinner_canvas = tk.Canvas(
      center_box, 
      width=60, 
      height=60, 
      bg="#111111", 
      highlightthickness=0
    )
    self.spinner_canvas.pack(pady=10)

    self.status_lbl = Label(
      center_box, 
      text="AI COPILOT IS WORKING\nGenerating secure cryptographic content, please wait...", 
      font=('Arial', 11, 'bold'), 
      foreground="#ffffff", 
      background="#111111", 
      justify="center", 
      anchor="center"
    )
    self.status_lbl.pack(pady=5)
    
    self.angle_step = 0
    self.animate_spinner()

  def animate_spinner(self):
    """ Generates a smooth, native non-blocking vector rotation loop """
    if not self.winfo_exists():
      return
        
    # Clear the previous drawing frame to prevent memory accumulation leaks
    self.spinner_canvas.delete("all")
    
    # Calculate the active starting angle offset frame
    start_angle = (self.angle_step * 24) % 360
    
    # Draw the primary background matte tracking track ring
    self.spinner_canvas.create_oval(
      6, 6, 54, 54, 
      outline="#252526", 
      width=3
    )
    
    # Render the active accent loading arc highlight
    self.spinner_canvas.create_arc(
      6, 6, 54, 54, 
      start=start_angle, 
      extent=90, 
      style="arc", 
      outline="#3fa8a5", 
      width=4,
      activedash=None
    )
    
    self.angle_step += 1
        
    # Ticks every 45ms for an incredibly fluid, hardware-accelerated motion effect
    self.after(45, self.animate_spinner)