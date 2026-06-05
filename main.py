#! /usr/bin/python3.11

import tkinter as tk
from tkinter.messagebox import askyesno

# 🛡️ ONLY import lightweight modules that do NOT depend on pycryptodome globally!
from config_files.progress import Progress_Frame
from config_files.styles import Stylings

def run_dependency_check():
    """
    Launches the standalone progress bar window using a separate temporary root.
    Returns True if we are safe to proceed to the main app.
    """
    installer_root = tk.Tk()
    app = Progress_Frame(installer_root)
    
    # Short-circuit immediately if all packages are already verified
    if not app.missing_modules:
        installer_root.destroy()
        return True

    installer_root.mainloop()
    return app.p_result.get()


def create_main_app():
    # 🚚 LAZY IMPORTS: Load heavy database/encryption components safely here
    from extras.models import verifyCookie, logout_func
    from app_files.run_cookie import Run_Cookie
    from app_files.welcome import welcome_frame
    from tabs.base_frame_tab import base_frame_tab

    session_cookie = verifyCookie()
    
    root = tk.Tk()
    root.title('Cryptor App')
    root.resizable(0, 0)
    
    # Track the background loop id cleanly on root to prevent console error output on exit
    root.check_run_id = None 

    # Styles
    Stylings(root)

    # The icon 
    try: 
        root.wm_iconbitmap("cryp.ico") 
    except: 
        pass

    def lgt():
        # Clear out our background loop timers before destroying the frame structure
        if root.check_run_id is not None:
            root.after_cancel(root.check_run_id)
            root.check_run_id = None

        if session_cookie is not None:
            if askyesno('Exiting...', 'The programme is shutting down now. All unsaved data may be lost permanently. You will be logged out automatically. \n\nDo you wish to proceed?'):
                logout_func(session_cookie[0])
                root.destroy()
        else:
            root.destroy()

    def check_run():
        Run_Cookie(root, session_cookie, create_main_app)
        # Always capture the dynamic loop id assignment reference
        root.check_run_id = root.after(1000, check_run)

    root.columnconfigure(0, weight=1)
    root.protocol("WM_DELETE_WINDOW", lgt)

    # 🚀 Clean Application Branching Routing
    if session_cookie is not None:
        root.check_run_id = root.after(1000, check_run)
        base = base_frame_tab(root, session_cookie, create_main_app)
        base.pack(fill='both', expand=1)
    else:
        welcome = welcome_frame(root, create_main_app)
        welcome.pack(fill='both', expand=1)

    root.mainloop()


#### RUN THE MAIN FUNCTION ####
if __name__ == "__main__":
    # 1. Run the safe standard-library dependency visual checkpoint FIRST
    proceed_to_app = run_dependency_check()
    
    # 2. Only pull in the database and frame setups if dependencies are verified
    if proceed_to_app:
        print("Dependencies verified. Initializing secure application database engines...")
        from extras.init_run import run_connection
        
        # Connect to your SQL instance
        run_connection()
        
        # Launch the fully isolated app environment
        create_main_app()
    else:
        print("Application startup terminated by user.")