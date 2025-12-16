import os
import sys

# Add the project root directory to the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import customtkinter as ctk
from base_header import BaseHeader
from mainpage_ui import MainPage
from login_ui import LogInWindow as LoginPage
from register_ui import SignupPage  


def center_top_window(window, top_padding=0):
    window.update_idletasks()

    w = window.winfo_width()
    h = window.winfo_height()

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    x = (screen_w // 2) - (w // 2)
    y = top_padding  

    window.geometry(f"{w}x{h}+{x}+{y}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Campus E-Wallet")
        self.geometry("1920x900")
        self.resizable(True, True)

        center_top_window(self, top_padding=50)

        # Main container for all screen 
        self.container = ctk.CTkFrame(self, fg_color="#CAF1C8")
        self.container.pack(fill="both", expand=True)

        # Load MainPage on start
        self.switch_page("main_page")

        self.after(10, lambda: center_top_window(self, top_padding=0))

        from system_backend.login import LoginSystem

        self.login_system = LoginSystem()
        
        # Ensure the main window closes the application properly
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # Global Page Switcher
    def switch_page(self, page_name, *args):
        """
        Universal page loader.
        This function clears the root container and loads any page.
        """
        # Destroy existing page
        for widget in self.container.winfo_children():
            widget.destroy()

        # Router
        if page_name == "main_page":
            page = MainPage(self.container, switch_page=self.switch_page)

        
        elif page_name == "login_page":
            page = LoginPage(
                parent=self.container,
                switch_page=self.switch_page,
                login_system=self.login_system
            )

        elif page_name == "signup_page":
            try:
                from register_ui import SignupPage
                page = SignupPage(self.container, switch_page=self.switch_page)
            except ImportError:
                print("[WARNING] SignupPage not implemented yet.")
                return

        else:
            print(f"[ERROR] Unknown page: {page_name}")
            return

        # Show page
        page.pack(fill="both", expand=True)

if __name__ == "__main__":
    App().mainloop()