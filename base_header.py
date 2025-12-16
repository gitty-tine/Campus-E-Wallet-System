import customtkinter as ctk
from PIL import Image
import os, sys

ctk.set_appearance_mode("light")

logo_path = r"C:\semproj_images\logo_wobg.png"

def safe_load_image(path, size):
    try:
        img = Image.open(path).resize(size)
        return ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=size
        )
    except Exception as e:
        print("IMAGE LOAD ERROR:", e)
        return None

class BaseHeader(ctk.CTkFrame):
    """
    Reusable Header for:
      - MainPage
      - LoginPage
      - SignupPage
      - Dashboard redirect pages

    Supports:
      - open_signup
      - open_login
      - switch_page (for back/home buttons)
      - show_back (bool)
      - show_home (bool)
    """

    def __init__(
        self,
        parent,
        open_signup=None,
        open_login=None,
        logo_path=None,
        switch_page=None,
        show_back=False,
        show_home=False
    ):
        super().__init__(parent, fg_color="#CAF1C8")

        self.open_signup = open_signup
        self.open_login = open_login
        self.logo_path = logo_path
        self.switch_page = switch_page
        self.show_back = show_back
        self.show_home = show_home

        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="#E6F4EA", height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        # WRAPPER for aligning left + right using pack
        wrapper = ctk.CTkFrame(header, fg_color="transparent")
        wrapper.pack(fill="x", pady=10, padx=20)

        # LEFT SIDE
        left = ctk.CTkFrame(wrapper, fg_color="transparent")
        left.pack(side="left")

        if self.logo_path:
            logo = safe_load_image(self.logo_path, (100, 100))
            if logo:
                ctk.CTkLabel(left, image=logo, text="").pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            left,
            text="Campus E-Wallet",
            font=("Times New Roman", 28)
        ).pack(side="left")

        # RIGHT SIDE (BUTTONS)
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.place(relx=0.985, rely=0.5, anchor="e")

        # Back Button
        if self.show_back and self.switch_page:
            ctk.CTkButton(
                right,
                text="← Back",
                fg_color="#b8d8b8",
                text_color="black",
                width=100,
                command=lambda: self.switch_page("main_page")
            ).pack(side="left", padx=10)

        #Home Button
        if self.show_home and self.switch_page:
            ctk.CTkButton(
                right,
                text="🏠 Home",
                fg_color="#87d087",
                text_color="black",
                width=100,
                command=lambda: self.switch_page("main_page")
            ).pack(side="left", padx=10)

        #Sign Up
        if self.open_signup:
            ctk.CTkButton(
                right, text="Sign Up",
                fg_color="#7AC28A",
                hover_color="#5EA973",
                text_color="black",
                width=120, height=40,
                command=self.open_signup
            ).pack(side="left", padx=10)

        # Login
        if self.open_login:
            ctk.CTkButton(
                right, text="Login",
                fg_color="#7AC28A",
                hover_color="#5EA973",
                text_color="black",
                width=120, height=40,
                command=self.open_login
            ).pack(side="left", padx=10)
