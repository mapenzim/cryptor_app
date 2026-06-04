import tkinter as tk
from tkinter.ttk import *
import time

class ClockFrame(LabelFrame):
    def __init__(self, master):
        super().__init__(master)
        self['text'] = 'Clock'

        self.label = Label(
            self,
            style='Clock.TLabel',
            text=self.time_string(),
            font=('Digital-7', 16))
        
        self.label.pack(expand=True, fill='both')

        #  Lay out the widget structure ONCE right here at startup
        self.grid(row=4, column=0, padx=5, pady=(5,50), ipady=5)

        # Schedule the first custom update loop
        self.label.after(1000, self.update_clock)

    def time_string(self):
        hr = time.strftime('%H')
        mn = time.strftime('%M')
        sc = time.strftime('%S')
        return f'{hr} hr\n{mn} min\n{sc} s'
      
    def update_clock(self):
        """ Custom update loop that safely respects the Tkinter lifecycle """
        # 🛡️ Safety check: If the clock label or its window was destroyed, exit loop
        if not self.winfo_exists() or not self.label.winfo_exists():
            return

        self.label.configure(text=self.time_string())

        # Schedule another timer safely using our renamed method
        self.label.after(1000, self.update_clock)