import sys
import os
import re
import time
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage

# Adjust path to project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

from system_backend.login import LoginSystem
from system_backend.students_wallet import StudentWallet
from system_backend.organization_wallet import OrganizationWallet 
from StudentDashboardSample import StudentDashboard, StudentOrganizationDashboard
from finance_admin_ui import App as FinanceAdminDashboardApp 

# Settings
APP_WIDTH = 1920
APP_HEIGHT = 900
LOGO_PATH = r"C:\semproj_images\logo_wobg.png"

ctk.set_appearance_mode("light")

# Safe Image Loader
def safe_load_image(path, size=None):
    try:
        if not os.path.exists(path):
            return CTkImage(Image.new("RGBA", (size or (50,50))), size=size)
        img = Image.open(path)
        return CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as e:
        print(f"Failed to load image '{path}': {e}")
        return CTkImage(Image.new("RGBA", (size or (50,50))), size=size)


# Main Window for Login
class LogInWindow(ctk.CTkFrame):
    def __init__(self, parent, switch_page, login_system):
        super().__init__(parent, fg_color="#CAF1C8")
        self.switch_page = switch_page
        self.login_system = login_system

        self.locked_until = None
        self.local_attempts = 0
        self.current_id = None
        self.verification_code = None

        self.build_ui()

    def build_ui(self):
        root = ctk.CTkFrame(self, fg_color="#CAF1C8")
        root.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(root, fg_color="#E6F4EA", height=150)
        header.pack(fill="x")
        header.pack_propagate(False)

        left_wrapper = ctk.CTkFrame(header, fg_color="transparent")
        left_wrapper.place(relx=0.01, rely=0.5, anchor="w")
        logo = safe_load_image(LOGO_PATH, (110, 104))
        if logo:
            ctk.CTkLabel(left_wrapper, image=logo, text="").pack(side="left", padx=10)
        ctk.CTkLabel(left_wrapper, text="Campus E-Wallet", font=("Times New Roman", 28)).pack(side="left", padx=(0,20))

        # Back Button
        right_wrapper = ctk.CTkFrame(header, fg_color="transparent")
        right_wrapper.place(relx=0.99, rely=0.5, anchor="e")
        ctk.CTkButton(
            right_wrapper,
            text="← Back to Main Page",
            height=40,
            command=lambda: self.switch_page("main_page")
        ).pack(padx=20)


        # Center Container
        center_wrapper = ctk.CTkFrame(root, fg_color="transparent")
        center_wrapper.place(relx=0.5, rely=0.55, anchor="center")

        ctk.CTkLabel(center_wrapper, text="Log in", font=("Times New Roman", 30, "bold"), text_color="#020202").pack(pady=(0,17))

        card = ctk.CTkFrame(center_wrapper, fg_color="#EBFFEA", corner_radius=30, width=500, height=350)
        card.pack()
        card.pack_propagate(False)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # ID and Password
        self.id_entry = ctk.CTkEntry(content, placeholder_text="Enter ID", font=("Times New Roman", 13), width=375, height=40)
        self.id_entry.pack(pady=(45, 4))
        self.password_entry = ctk.CTkEntry(content, placeholder_text="Enter Password", font=("Times New Roman", 13), width=375, height=40, show="*")
        self.password_entry.pack(pady=(15, 4))

        # Show password checkbox
        self.show_var = tk.IntVar()
        ctk.CTkCheckBox(content, text="Show Password", font=("Times New Roman", 13), variable=self.show_var, command=self._toggle_password).pack(pady=(20,8))

        # Login button
        self.login_btn = ctk.CTkButton(content, text="Login", font=("Times New Roman", 13), hover_color="#8EC78B", text_color="black", fg_color="#CAF1C8", width=189, height=35, command=self.handle_login)
        self.login_btn.pack(pady=(4,6))

        # Attempts & Lock labels
        self.attempts_label = ctk.CTkLabel(content, text="", font=("Times New Roman",12))
        self.attempts_label.pack(pady=(0,5))
        self.lock_label = ctk.CTkLabel(content, text="", font=("Times New Roman",12))
        self.lock_label.pack()

        # Forgot password
        ctk.CTkButton(content, text="Forgot Password?", fg_color="transparent", font=("Times New Roman", 13), hover_color="#8EC78B", text_color="black", command=self.open_forgot_popup).pack(pady=(0, 45))

    # Password toggle
    def _toggle_password(self):
        self.password_entry.configure(show="" if self.show_var.get() else "*")

    # Handle login
    def handle_login(self):
        user_id = self.id_entry.get().strip()
        pw = self.password_entry.get()

        if not user_id or not pw:
            messagebox.showerror("Error", "Fill all fields.")
            return

        if not re.match(r"^[A-Za-z0-9_-]+$", user_id):
            messagebox.showerror("Error", "Invalid ID format.")
            return

        res = self.login_system.login(user_id, pw)
        if res["ok"]:

    # Force first-time login users (admin-created) to reset password
            if res.get("data", {}).get("must_change_password"):
                # Disable everything else in the main window until password is set
                self.login_btn.configure(state="disabled")
                self.id_entry.configure(state="disabled")
                self.password_entry.configure(state="disabled")
                FirstTimeSetPasswordWindow(self, user_id)
            else:
                user_data = res["data"]
                messagebox.showinfo("Login Successful", "Welcome to Campus E-Wallet!")
                self.open_dashboard(user_data)

        else:
            rem = res.get("data", {}).get("remaining_attempts")
            if rem is not None:
                self.attempts_label.configure(text=f"Wrong password. {rem} attempts left.")
            if "locked" in res["msg"].lower():
                secs = int(re.search(r"\d+", res["msg"]).group())
                self.start_lockout(secs)
            messagebox.showerror("Login Failed", res["msg"])

    # Lockout countdown
    def start_lockout(self, seconds: int):
        self.locked_until = time.time() + seconds
        self.login_btn.configure(state="disabled")

        def countdown():
            while True:
                remaining = int(self.locked_until - time.time())
                if remaining <= 0:
                    self.locked_until = None
                    self.login_btn.after(0, lambda: self.login_btn.configure(state="normal"))
                    self.lock_label.after(0, lambda: self.lock_label.configure(text=""))
                    self.attempts_label.after(0, lambda: self.attempts_label.configure(text=""))
                    break
                mins, secs = divmod(remaining, 60)
                text = f"Login disabled. Try again in {mins}:{secs:02d}"
                self.lock_label.after(0, lambda t=text: self.lock_label.configure(text=t))
                time.sleep(1)

        threading.Thread(target=countdown, daemon=True).start()

    # Open forgot password popup
    def open_forgot_popup(self):
        ForgotPasswordWindow(self)

    # Mainpage after login
    def open_mainpage(self):
        self.switch_page("main_page")  # Assuming main_page is the dashboard or appropriate page

    # Open dashboard window
    def open_dashboard(self, user_data):
        # Hide the main app window instead of destroying it
        main_app = self.master.master
        main_app.withdraw()

        # Choose dashboard based on user role
        role = user_data.get("role", "").lower()

        if role == "finance admin":
            # Instantiate and run the Finance Admin UI
            dashboard = FinanceAdminDashboardApp()
            # Pass the logged-in admin's user_id to the finance admin app
            if hasattr(dashboard, 'admin_user_id'):
                dashboard.admin_user_id = user_data.get("user_id")

        elif role == "treasurer":
            # For treasurers, we need both the student and organization backends
            student_backend = StudentWallet(user_id=user_data["user_id"])
            # The OrganizationWallet needs the student_id, not the user_id
            org_backend = OrganizationWallet(student_id=user_data["student_id"])
            dashboard = StudentOrganizationDashboard(student_backend, user_data, org_backend)

        else: # Default to student/personal
            student_backend = StudentWallet(user_id=user_data["user_id"])
            dashboard = StudentDashboard(student_backend, user_data)

        # Make the dashboard modal and wait for it to be closed
        dashboard.grab_set()  # Directs all events to the dashboard
        dashboard.wait_window() # Pauses the code here until the dashboard is destroyed

        # When the dashboard is closed, show the main app window again and switch to the main page
        main_app.deiconify()
        main_app.switch_page("main_page")

# Setting Password for First Time Account
class FirstTimeSetPasswordWindow(ctk.CTkToplevel):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id
        self.title("Set Your Password")
        w, h = 480, 320
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 3
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(fg_color="#E7F6E7")
        self.resizable(False, False)
        self.grab_set()

        box = ctk.CTkFrame(self, fg_color="#F1FFF1", width=400, height=250)
        box.pack(expand=True, pady=20)
        box.pack_propagate(False)

        ctk.CTkLabel(box, text="Set your new password", font=("Times New Roman", 16, "bold")).pack(pady=(20,10))

        self.p1 = ctk.CTkEntry(box, placeholder_text="New Password", width=260, show="*")
        self.p1.pack(pady=(5,5))
        self.p2 = ctk.CTkEntry(box, placeholder_text="Confirm Password", width=260, show="*")
        self.p2.pack(pady=(5,5))

        self.show_pw_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(box, text="Show Password", variable=self.show_pw_var, command=self.toggle_password).pack(pady=(5,10))

        ctk.CTkButton(box, text="Set Password", width=150, fg_color="#4DAF4F", command=self.set_password).pack(pady=10)

    def toggle_password(self):
        show = self.show_pw_var.get()
        self.p1.configure(show="" if show else "*")
        self.p2.configure(show="" if show else "*")

    def set_password(self):
        p1, p2 = self.p1.get(), self.p2.get()
        res = self.master.login_system.reset_password(self.user_id, p1, p2, force_change=True)
        if res["ok"]:
            messagebox.showinfo("Success", "Password set successfully! Please log in again.")
            # Re-enable main login fields
            self.master.login_btn.configure(state="normal")
            self.master.id_entry.configure(state="normal")
            self.master.password_entry.configure(state="normal")
            self.destroy()  # Close popup
            self.master.id_entry.delete(0, "end")
            self.master.password_entry.delete(0, "end")
        else:
            messagebox.showerror("Error", res["msg"])


# Forgot Password Popup
class ForgotPasswordWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Forgot Password")
        w,h = 480,420
        x = (self.winfo_screenwidth()-w)//2
        y = (self.winfo_screenheight()-h)//3
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(fg_color="#E7F6E7")
        self.resizable(False, False)
        self.grab_set()

        self.current_id = None
        self.timer_running = False

        self.container = ctk.CTkFrame(self, fg_color="#E7F6E7")
        self.container.pack(fill="both", expand=True)

        self.show_page(StepEnterID)

    def show_page(self, PageClass):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.current_page = PageClass(self.container, self)


# Step 1 - Enter ID
class StepEnterID(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#E7F6E7")
        self.controller = controller
        self.pack(fill="both", expand=True)

        box = ctk.CTkFrame(self, fg_color="#E7F6E7", width=350, height=230)
        box.pack(expand=True, pady=10)
        box.pack_propagate(False)

        ctk.CTkLabel(box, text="Search for ID").pack(pady=(15,5))
        self.entry = ctk.CTkEntry(box, placeholder_text="Enter your ID", width=260)
        self.entry.pack(pady=(20,10))

        ctk.CTkButton(box, text="Send Code", width=120, fg_color="#4DAF4F", command=self.send_code).pack(pady=(5,10))

        self.timer_label = ctk.CTkLabel(box, text="")
        self.timer_label.pack()
        self.error_label = ctk.CTkLabel(box, text="", text_color="red")
        self.error_label.pack(pady=(5,10))

    def send_code(self):
        student_id = self.entry.get().strip()
        res = self.controller.master.login_system.forgot_password_request(student_id)
        if res["ok"]:
            self.controller.current_id = student_id
            self.controller.show_page(StepVerifyCode)
        else:
            self.error_label.configure(text=res["msg"])


# Step 2 - Verify Code
class StepVerifyCode(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#E7F6E7")
        self.controller = controller
        self.pack(fill="both", expand=True)

        box = ctk.CTkFrame(self, fg_color="#F1FFF1", width=350, height=230)
        box.pack(expand=True, pady=10)
        box.pack_propagate(False)

        ctk.CTkLabel(box, text="Verification Code").pack(pady=(15,10))

        self.entry = ctk.CTkEntry(box, placeholder_text="Enter 6-digit code", width=200)
        self.entry.pack(pady=10)

        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(pady=5)
        self.resend_btn = ctk.CTkButton(row, text="Resend", width=100, fg_color="#52b155", command=self.start_resend_timer)
        self.resend_btn.pack(side="left", padx=10)
        self.verify_btn = ctk.CTkButton(row, text="Verify", width=100, fg_color="#52b155", command=self.verify_code)
        self.verify_btn.pack(side="left", padx=10)

        self.timer_label = ctk.CTkLabel(box, text="")
        self.timer_label.pack(pady=(5,0))

        self.error_label = ctk.CTkLabel(box, text="", text_color="red")
        self.error_label.pack(pady=(5,10))

    def start_resend_timer(self):
        # Attempt to resend the code
        res = self.controller.master.login_system.forgot_password_request(self.controller.current_id)
        if res["ok"]:
            # start countdown
            self.remaining = 30
            self.resend_btn.configure(state="disabled")
            self.update_timer()
            self.timer_label.configure(text="Verification code resent. Check your email.", text_color="green")
        else:
            self.timer_label.configure(text=res["msg"], text_color="red")

    def update_timer(self):
        if self.remaining > 0:
            self.timer_label.configure(text=f"Wait {self.remaining}s to resend")
            self.remaining -= 1
            self.after(1000, self.update_timer)
        else:
            self.timer_label.configure(text="")
            self.resend_btn.configure(state="normal")

    def verify_code(self):
        code = self.entry.get().strip()
        res = self.controller.master.login_system.verify_code(self.controller.current_id, code)
        if res["ok"]:
            self.controller.show_page(StepSetPassword)
        else:
            # Clear any previous timer message
            self.timer_label.configure(text="")
            # Show error message inside this frame
            self.error_label.configure(text=res["msg"])


# Step 3 - Set Password
class StepSetPassword(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#E7F6E7")
        self.controller = controller
        self.pack(fill="both", expand=True)

        box = ctk.CTkFrame(self, fg_color="#F1FFF1", width=350, height=260)
        box.pack(expand=True, pady=10)
        box.pack_propagate(False)

        self.p1 = ctk.CTkEntry(box, placeholder_text="New Password", width=260, show="*")
        self.p1.pack(pady=(5,5))
        self.p2 = ctk.CTkEntry(box, placeholder_text="Confirm Password", width=260, show="*")
        self.p2.pack(pady=(5,2))

        self.show_pw_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(box, text="Show Password", variable=self.show_pw_var, command=self.toggle_password).pack(pady=(10,10))

        ctk.CTkButton(box, text="Confirm", width=150, fg_color="#4DAF4F", command=self.reset_pass).pack(pady=10)

    def toggle_password(self):
        show = self.show_pw_var.get()
        self.p1.configure(show="" if show else "*")
        self.p2.configure(show="" if show else "*")

    def reset_pass(self):
        p1, p2 = self.p1.get(), self.p2.get()
        res = self.controller.master.login_system.reset_password(self.controller.current_id, p1, p2)
        if res["ok"]:
            self.controller.show_page(StepSuccess)
        else:
            messagebox.showerror("Error", res["msg"])


# Step 4 - Success
class StepSuccess(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#E7F6E7")
        self.controller = controller
        self.pack(fill="both", expand=True)

        box = ctk.CTkFrame(self, fg_color="#F1FFF1", width=350, height=230)
        box.pack(expand=True, pady=10)
        box.pack_propagate(False)

        ctk.CTkLabel(box, text="Password reset complete! You can now log in with your new password.", wraplength=280, justify="center").pack(pady=30)
        ctk.CTkButton(box, text="Return to Login", fg_color="#4CAF50", width=150, command=self.controller.destroy).pack(pady=20)


if __name__ == "__main__":
    app = LogInWindow()
    app.mainloop()