import sys
import os
import traceback
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image

from base_header import BaseHeader


# ensure project base dir 
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

from system_backend.registration import verify_student, verify_code, create_account

# Global Apperance
ctk.set_appearance_mode("light")


# Helpers
def is_verify_sent_message(msg: str) -> bool:
    """Robust heuristics to interpret backend message meaning 'sent'."""
    if not isinstance(msg, str):
        return False
    low = msg.lower()
    # accept a few common success markers
    return ("verification code sent" in low) or ("code sent" in low) or ("verification code resent" in low) or ("sent to your student" in low) or ("verification code" in low and "sent" in low)


# Minimal helper card
def make_card(parent, width=800, height=500, fg="#EBFFEA", corner_radius=20):
    card = ctk.CTkFrame(parent, width=width, height=height, corner_radius=corner_radius)
    card.pack_propagate(False)
    try:
        card.configure(fg_color=fg)
    except Exception:
        pass
    return card


# Back Button
class BackButton(ctk.CTkButton):
    def __init__(self, parent, command):
        super().__init__(
            parent,
            text="⬅",
            width=50,
            height=40,
            fg_color="#7AC28A",
            hover_color="#5EA973",
            text_color="black",
            corner_radius=10,
            font=("Times New Roman", 20, "bold"),
            command=command
        )


# Signup Page
class SignupPage(ctk.CTkFrame):
    def __init__(self, parent, switch_page):
        super().__init__(parent, fg_color="#CAF1C8")

        self.switch_page = switch_page
        self.pages = {}

        self.header = BaseHeader(
            self,
            open_login=lambda: self.switch_page("login_page"),
            open_signup=None
        )
        self.header.pack(fill="x")

        ctk.CTkButton(
            self,
            text="← Back to Main Page",
            height=35,
            command=lambda: self.switch_page("main_page")
        ).pack(pady=(10, 0))

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Register Sub-pages
        self.register_page("SearchIDPage", SearchIDPage)
        self.register_page("VerificationPage", VerificationPage)
        self.register_page("CreateAccountPage", CreateAccountPage)
        self.register_page("SuccessPage", SuccessPage)

        # Default starting page
        self.show_page("SearchIDPage")

    # Page Management Functions
    def register_page(self, name, page_class):
        """Create and store sub-pages but keep them hidden."""
        page = page_class(self.container)
        page.place(relx=0.5, rely=0.5, anchor="center")

        if hasattr(page, "hide"):
            page.hide()

        self.pages[name] = page
        return page

    def show_page(self, name):
        """Show selected registration step."""
        for page in self.pages.values():
            page.lower()

        target = self.pages.get(name)
        if target:
            target.lift()


# Step 1 -Search ID Page 
class SearchIDPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.app = parent.master
        self.student_id = None
        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Sign Up for an Account", font=("Times New Roman", 28, "bold"))
        title.pack(pady=(6, 20))

        self.card = make_card(self, width=720, height=320, corner_radius=20)
        self.card.pack()

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=24, pady=24)

        self.studentID = ctk.CTkEntry(inner, placeholder_text="Student ID", width=480, height=44,
                                      font=("Times New Roman", 16))
        self.studentID.pack(pady=(20, 10))

        self.searchBtn = ctk.CTkButton(inner, text="🔍 Search", width=160, height=44,
                                       fg_color="#7AC28A", command=self.handle_verify_student)
        self.searchBtn.pack()

        self.statusLabel = ctk.CTkLabel(inner, text="", font=("Times New Roman", 14))
        self.statusLabel.pack(pady=(12, 0))

    def show_message(self, text, status="error"):
        color = "#007700" if status == "success" else "#FF0000"
        self.statusLabel.configure(text=text, text_color=color)

    def handle_verify_student(self):
        student_id = self.studentID.get().strip()
        if not student_id:
            self.show_message("Please enter a Student ID", "error")
            return

        try:
            msg = verify_student(student_id)  # backend returns a single string
        except Exception as e:
            print("[ERROR] verify_student crashed:", e)
            traceback.print_exc()
            self.show_message("Backend error. Check console.", "error")
            return

        # Interpret backend message
        if is_verify_sent_message(msg):
            # success path
            self.show_message(msg, "success")
            self.student_id = student_id
            ver_page = self.app.pages["VerificationPage"]
            ver_page.set_student_id(student_id)
            self.app.show_page("VerificationPage")
        else:
            # failure / informative messages
            self.show_message(msg or "Unknown error.", "error")

# Step 2 - Verification Page
class VerificationPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.app = parent.master
        self.student_id = None
        self.remaining = 0     
        self._build_ui()

    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(4, 8))
        BackButton(top, command=lambda: self.app.show_page("SearchIDPage")).pack(anchor="w")

        title = ctk.CTkLabel(self, text="Verification", font=("Times New Roman", 22, "bold"))
        title.pack(pady=(2, 8))

        self.card = make_card(self, width=640, height=300, corner_radius=20)
        self.card.pack()

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=18, pady=18)

        center = ctk.CTkFrame(inner, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        self.codeEntry = ctk.CTkEntry(center, placeholder_text="Enter Verification Code",
                                      width=420, height=40, font=("Times New Roman", 16))
        self.codeEntry.pack(pady=(6, 8))

        self.statusLabel = ctk.CTkLabel(center, text="", font=("Times New Roman", 14))
        self.statusLabel.pack(pady=(6, 8))

        btn_row = ctk.CTkFrame(center, fg_color="transparent")
        btn_row.pack(pady=(6, 0))

        self.resendBtn = ctk.CTkButton(btn_row, text="Resend Code", width=160, height=40,
                                       command=self.handle_resend_code)
        self.resendBtn.pack(side="left", padx=8)

        self.sendBtn = ctk.CTkButton(btn_row, text="Send", width=120, height=40,
                                     command=self.handle_send_code)
        self.sendBtn.pack(side="left", padx=8)

    def set_student_id(self, student_id):
        self.student_id = student_id

    def show_message(self, text, status="error"):
        color = "#007700" if status == "success" else "#FF0000"
        self.statusLabel.configure(text=text, text_color=color)

    # Time Helpers
    def extract_wait_time(self, msg):
        """Extracts the 'X seconds' from backend message."""
        try:
            parts = msg.split()
            for word in parts:
                if word.isdigit():
                    return int(word)
        except:
            pass
        return None

    def start_timer(self, seconds):
        """Start countdown + disable button."""
        self.remaining = seconds
        self.resendBtn.configure(state="disabled")
        self.update_timer()

    def update_timer(self):
        if self.remaining <= 0:
            self.resendBtn.configure(text="Resend Code", state="normal")
            self.statusLabel.configure(text="You can now request a new code.", text_color="#007700")
            return

        # Resend Button
        self.resendBtn.configure(text=f"Resend ({self.remaining}s)")

        # Status Label Message
        self.statusLabel.configure(
            text=f"Please wait {self.remaining} seconds before requesting another code.",
            text_color="#FF0000"
        )

        self.remaining -= 1
        self.after(1000, self.update_timer)

    # Resend Code
    def handle_resend_code(self):
        if not self.student_id:
            self.show_message("No student ID available to resend.", "error")
            return

        try:
            msg = verify_student(self.student_id)
        except Exception as e:
            print("[ERROR] resend verify_student crashed:", e)
            traceback.print_exc()
            self.show_message("Backend error. Check console.", "error")
            return

        # CASE 1 — Backend says WAIT X seconds
        wait = self.extract_wait_time(msg)
        if wait is not None:
            self.show_message(msg, "error")
            self.start_timer(wait)
            return

        # CASE 2 — Code successfully sent
        if is_verify_sent_message(msg):
            self.show_message(msg, "success")
            self.start_timer(30)
            return

        # CASE 3 — Other backend errors
        self.show_message(msg or "Unknown response from backend.", "error")

   
    # Verifying Code
    def handle_send_code(self):
        code = self.codeEntry.get().strip()
        if not code:
            self.show_message("Please enter the verification code.", "error")
            return

        try:
            result = verify_code(self.student_id, code)
        except Exception as e:
            print("[ERROR] verify_code crashed:", e)
            traceback.print_exc()
            self.show_message("Backend error. Check console.", "error")
            return

        if isinstance(result, str):
            self.show_message(result, "error")
            return

        try:
            success, info = result
        except:
            self.show_message("Unexpected backend response.", "error")
            return

        if not success:
            msg = info if isinstance(info, str) else "Invalid verification code."
            self.show_message(msg, "error")
            return

        if not isinstance(info, dict):
            self.show_message("Unexpected backend data format.", "error")
            return

        name = info.get("name", "")
        email = info.get("email", "")

        create_page = self.app.pages["CreateAccountPage"]
        create_page.set_student_info(self.student_id, name, email)
        self.app.show_page("CreateAccountPage")


# Step 3 - Create an Account Page
class CreateAccountPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.app = parent.master
        self.student_id = None
        self.student_name = None
        self.student_email = None
        self._build_ui()

    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(4, 8))
        BackButton(top, command=lambda: self.app.show_page("VerificationPage")).pack(anchor="w")

        title = ctk.CTkLabel(self, text="Create Account", font=("Times New Roman", 22, "bold"))
        title.pack(pady=(6, 8))

        self.card = make_card(self, width=720, height=420, corner_radius=20)
        self.card.pack()

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=18, pady=18)

        self.nameBox = ctk.CTkEntry(inner, width=640, height=36, state="disabled", font=("Times New Roman", 14))
        self.nameBox.pack(pady=(6, 6))

        self.idBox = ctk.CTkEntry(inner, width=640, height=36, state="disabled", font=("Times New Roman", 14))
        self.idBox.pack(pady=(6, 6))

        self.emailBox = ctk.CTkEntry(inner, width=640, height=36, state="disabled", font=("Times New Roman", 14))
        self.emailBox.pack(pady=(6, 12))

        self.passwordInput = ctk.CTkEntry(inner, placeholder_text="Create Password", show="*", width=640,
                                          height=40, font=("Times New Roman", 14))
        self.passwordInput.pack(pady=(6, 6))

        self.confirmPasswordInput = ctk.CTkEntry(inner, placeholder_text="Confirm Password", show="*", width=640,
                                                 height=40, font=("Times New Roman", 14))
        self.confirmPasswordInput.pack(pady=(6, 6))

        self.show_password_var = ctk.BooleanVar(value=False)
        self.showPasswordCheck = ctk.CTkCheckBox(inner, text="Show Password", variable=self.show_password_var,
                                                command=self.toggle_password)
        self.showPasswordCheck.pack(pady=(6, 10))

        self.createBtn = ctk.CTkButton(inner, text="Create Account", width=320, height=40,
                                       fg_color="#7AC28A", command=self.handle_create_account)
        self.createBtn.pack(pady=(6, 10))

        self.statusLabel = ctk.CTkLabel(inner, text="", font=("Times New Roman", 14))
        self.statusLabel.pack(pady=(4, 0))

    def set_student_info(self, student_id, name, email):
        self.student_id = student_id
        self.student_name = name
        self.student_email = email

        self.nameBox.configure(state="normal")
        self.nameBox.delete(0, "end")
        self.nameBox.insert(0, name)
        self.nameBox.configure(state="disabled")

        self.idBox.configure(state="normal")
        self.idBox.delete(0, "end")
        self.idBox.insert(0, student_id)
        self.idBox.configure(state="disabled")

        self.emailBox.configure(state="normal")
        self.emailBox.delete(0, "end")
        self.emailBox.insert(0, email)
        self.emailBox.configure(state="disabled")

    def toggle_password(self):
        mode = "" if self.show_password_var.get() else "*"
        self.passwordInput.configure(show=mode)
        self.confirmPasswordInput.configure(show=mode)

    def show_message(self, text, status="error"):
        color = "#007700" if status == "success" else "#FF0000"
        self.statusLabel.configure(text=text, text_color=color)

    def handle_create_account(self):
        if not self.student_id:
            self.show_message("No student selected. Complete verification first.", "error")
            return

        password = self.passwordInput.get().strip()
        confirm = self.confirmPasswordInput.get().strip()
        if not password or not confirm:
            self.show_message("Please fill both password fields.", "error")
            return

        try:
            success, msg = create_account(self.student_id, password, confirm)
        except Exception as e:
            print("[ERROR] create_account crashed:", e)
            traceback.print_exc()
            self.show_message("Backend error. Check console.", "error")
            return

        if success:
            self.show_message(msg or "Account created.", "success")
            success_page = self.app.pages["SuccessPage"]
            success_page.set_message(msg or "Account created successfully!")
            self.app.show_page("SuccessPage")
        else:
            self.show_message(msg or "Failed to create account.", "error")


# Step 4 - Success Page
class SuccessPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.app = parent.master
        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Success", font=("Times New Roman", 22, "bold"))
        title.pack(pady=(6, 12))

        self.card = make_card(self, width=640, height=320, corner_radius=20)
        self.card.pack()

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=18, pady=18)

        self.statusLabel = ctk.CTkLabel(inner, text="Successfully Created!", font=("Times New Roman", 16, "bold"))
        self.statusLabel.pack(pady=(6, 8))

        try:
            img = CTkImage(
                light_image=Image.open(r"C:\semproj_images\checked.png"),
                size=(120, 120)
            )

            self.img_label = ctk.CTkLabel(inner, image=img, text="")
            self.img_label.image = img  # prevent garbage collection
            self.img_label.pack(pady=(6, 8))

        except Exception as e:
            print("Image Load Error:", e)
            pass

        self.loginBtn = ctk.CTkButton(inner, text="Go to Login", width=240, height=40,
                                      fg_color="#7AC28A", command=self.go_to_login)
        self.loginBtn.pack(pady=(6, 8))

    def set_message(self, message):
        self.statusLabel.configure(text=message)

    def go_to_login(self):
        try:
            self.app.show_page("LoginPage")
        except Exception:
            # fallback: close window
            try:
                self.app.destroy()
            except Exception:
                pass

def main():
    app = SignupPage()
    app.mainloop()

if __name__ == "__main__":
    main()
