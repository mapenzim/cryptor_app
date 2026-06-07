import sys
import subprocess
import tkinter as tk
from tkinter.ttk import Progressbar, Frame, Button
from threading import Thread
from importlib.metadata import distributions

class Download_Module(Thread):
    def __init__(self, modules_to_install):
        super().__init__()
        self.modules_to_install = modules_to_install
        self.process_output = None
        self.success = False

    def run(self):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--ignore-installed"] + self.modules_to_install,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            self.process_output = result.stdout
            self.success = (result.returncode == 0)
        except Exception as e:
            self.process_output = str(e)
            self.success = False


class Progress_Frame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.p_result = tk.BooleanVar(value=False)

        master.geometry("340x180") 
        master.attributes('-topmost', True)
        master.title("Installing Dependencies")
        master.resizable(0, 0)

        self.progress_frame = Frame(self)
        self.progress_frame.pack(fill=tk.X, padx=15, pady=15)

        # 1. Changed mode to 'determinate' so we can explicitly control the value (0 to 100)
        self.progress_bar = Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL, 
            length=300, 
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, expand=True)

        # 2. Add a label specifically to display the string percentage text
        self.percent_label = tk.Label(self, text="0%", font=("Arial", 10, "bold"), fg="#2bc475")
        self.percent_label.pack(anchor='e', padx=17)

        self.status_label = tk.Label(
            self, 
            text="Required modules missing. Click below to install.", 
            font=("Arial", 9),
            wraplength=300,
            justify="left"
        )
        self.status_label.pack(anchor='w', padx=17, pady=(0, 10))

        self.buttons = Frame(self)
        self.buttons.pack(side='bottom', fill=tk.X, padx=15, pady=10)

        self.YesBtn = Button(self.buttons, text="Download Modules", command=self.check_and_start)
        self.YesBtn.pack(side='left', expand=True, fill=tk.X, padx=(0, 5))

        self.SkipBtn = Button(self.buttons, text='Skip', command=self.skip_dwn)
        self.SkipBtn.pack(side='right', expand=True, fill=tk.X, padx=(5, 0))
        
        self.required_modules = {'pycryptodome'} 
        self.installed_modules = {dist.metadata['Name'].lower() for dist in distributions()}
        self.missing_modules = [pkg for pkg in self.required_modules if pkg not in self.installed_modules]

        self.pack(fill='both', expand=True)

        if not self.missing_modules:
            self.p_result.set(True)
            self.status_label.config(text="All modules verified! Launching...")
            self.YesBtn['state'] = "disabled"
            self.master.after(500, self.skip_dwn)

    def skip_dwn(self):
        self.p_result.set(True)
        self.master.destroy()

    def check_and_start(self):
        if self.missing_modules:
            self.YesBtn['state'] = "disabled"
            self.SkipBtn['state'] = "disabled"
            self.master.update_idletasks() 
            self.handle_download()

    def handle_download(self):
        self.status_label.config(text="Running pip install... This may take a moment.")
        self.master.update()

        download_thread = Download_Module(self.missing_modules)
        download_thread.start()

        # Begin monitoring the thread and executing the progressive visual simulation
        self.monitor(download_thread)

    def monitor(self, download_thread):
        if download_thread.is_alive():
            # Get current bar position
            current_val = self.progress_bar['value']
            
            # Simulate progress: slowly tick up to 95% while waiting on pip
            if current_val < 95:
                # Increments slightly faster early on, slower as it approaches 95%
                new_val = current_val + (1.5 if current_val < 50 else 0.4)
                self.progress_bar['value'] = new_val
                self.percent_label.config(text=f"{int(new_val)}%")
            
            self.master.update_idletasks()
            self.after(100, lambda: self.monitor(download_thread))
        else:
            if download_thread.success:
                # Pip successfully completed! Force the bar immediately to 100%
                self.progress_bar['value'] = 100
                self.percent_label.config(text="100%")
                self.status_label.config(text="Installation complete! Launching...")
                self.master.update()
                
                # Give the user 400 milliseconds to actually see the 100% before closing
                self.after(400, self.close_after_success)
            else:
                self.status_label.config(text="Installation failed! Check console.")
                print("--- PIP ERROR LOG ---")
                print(download_thread.process_output)
                self.SkipBtn['state'] = "normal"

    def close_after_success(self):
        self.p_result.set(True)
        self.master.destroy()