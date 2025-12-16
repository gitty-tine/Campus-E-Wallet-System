import customtkinter as ctk
from PIL import Image
from base_header import BaseHeader


class MainPage(ctk.CTkFrame):
    def __init__(self, parent, switch_page):
        super().__init__(parent, fg_color="#CAF1C8")

        self.switch_page = switch_page
        self.initUI()

    def load_image(self, path, size):
        try:
            img = Image.open(path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print(f"Failed to load image '{path}': {e}")
            return ctk.CTkImage(Image.new("RGBA", size), size=size)

    def initUI(self):
        header = BaseHeader(
            self,
            open_login=lambda: self.switch_page("login_page"),
            open_signup=lambda: self.switch_page("signup_page"),
            logo_path=r"C:\semproj_images\logo_wobg.png"
        )
        header.pack(fill="x")

        # Center Content
        centerFrame = ctk.CTkFrame(self, fg_color="transparent")
        centerFrame.pack(expand=True, fill="both")

        centerFrame.grid_rowconfigure(0, weight=1)
        centerFrame.grid_columnconfigure(0, weight=1)
        centerFrame.grid_columnconfigure(1, weight=1)

        # Mainpage Image Left Side
        img_main = self.load_image(r"C:\semproj_images\Header-png.png", (600, 725))

        img_label = ctk.CTkLabel(centerFrame, image=img_main, text="")
        img_label.grid(row=0, column=0, sticky="e", padx=(100, 100))

        # Mainpage Right Side Text
        textFrame = ctk.CTkFrame(centerFrame, fg_color="transparent")
        textFrame.grid(row=0, column=1, sticky="w", padx=(100, 100))

        # Title
        ctk.CTkLabel(
            textFrame,
            text="Campus E-Wallet",
            font=("Times New Roman", 50, "bold"),
            text_color="black"
        ).pack(anchor="w", pady=(10, 10))

        # Justified Paragraph Description
        paragraph = (
            "The Campus E-Wallet Management System is a digital payment and fund "
            "management platform designed to help students and administrators "
            "manage campus financial transactions easily and securely."
        )

        def justify_text(text, line_length=50):
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                if sum(len(w) for w in current_line) + len(current_line) + len(word) <= line_length:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]

            lines.append(" ".join(current_line))
            return "\n".join(lines)

        justified_text = justify_text(paragraph)

        ctk.CTkLabel(
            textFrame,
            text=justified_text,
            font=("Times New Roman", 23),
            text_color="black",
            anchor="w",
            justify="left"
        ).pack(anchor="w", pady=5)


        # Footer
        footer = ctk.CTkFrame(self, height=85, fg_color="#4D5E4B", corner_radius=0)
        footer.pack(fill="x", side="bottom")

        ctk.CTkLabel(
            footer, text="Contact Us",
            font=("Times New Roman", 23, "bold"),
            text_color="white"
        ).place(x=40, y=15)

        ctk.CTkLabel(
            footer, text="campus.ewallet@gmail.com",
            font=("Times New Roman", 20),
            text_color="white"
        ).place(x=40, y=45)