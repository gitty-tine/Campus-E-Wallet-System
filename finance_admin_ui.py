import customtkinter as ctk
from tkinter import messagebox, simpledialog
from system_backend.finance_admin_wallet import FinanceAdminWallet

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


# Main Window for Finance Admin
class App(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Campus E-Wallet System - Finance Admin")
        self.geometry("1000x600")
        self.admin_user_id = None  # store the logged-in finance admin id

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (FinanceAdminDashboard, CreateStudentPage,
                  CashInPage, CashInDetailPage,
                  CashOutPage, CashOutDetailPage, TransactionsPage): # Removed App from here
            frame = F(container, self.show_frame)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("FinanceAdminDashboard")

    def show_frame(self, page_name, data=None):
        frame = self.frames[page_name]

        # If the frame accepts admin_user_id, set it
        if hasattr(frame, "admin_user_id"):
            frame.admin_user_id = self.admin_user_id

        frame.tkraise()

        # Load data if the frame has load_data method and data is passed
        if data and hasattr(frame, "load_data"):
            frame.load_data(data)

    def logout(self):
        """Destroys the dashboard window to return to the main application."""
        self.destroy()


# Finance Admin Dashboard
class FinanceAdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, switch_callback):
        super().__init__(parent)
        self.switch_callback = switch_callback
        self.grid_columnconfigure(0, weight=1)

        logout_btn = ctk.CTkButton(
            self,
            text="Logout",
            command=lambda: self.master.master.logout()
        )
        logout_btn.place(relx=0.98, rely=0.05, anchor="ne")

        header = ctk.CTkLabel(self, text="Finance Admin Dashboard",
                               font=ctk.CTkFont(size=28, weight="bold"))
        header.pack(pady=20)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=40, padx=20, fill="x")
        for i in range(4):
            btn_frame.grid_columnconfigure(i, weight=1, uniform="btn_col")

        create_btn = ctk.CTkButton(btn_frame, text="🧑‍🎓\nCreate Student\nAccount",
                                   width=200, height=150,
                                   command=lambda: switch_callback("CreateStudentPage"))
        create_btn.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        cashin_btn = ctk.CTkButton(btn_frame, text="💰\nView Cash-In\nRequests",
                                   width=200, height=150,
                                   command=lambda: switch_callback("CashInPage"))
        cashin_btn.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        cashout_btn = ctk.CTkButton(btn_frame, text="🏦\nView Cash-Out\nRequests",
                                    width=200, height=150,
                                    command=lambda: switch_callback("CashOutPage"))
        cashout_btn.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        transactions_btn = ctk.CTkButton(btn_frame, text="📜\nView\nTransactions",
                                         width=200, height=150,
                                         command=lambda: switch_callback("TransactionsPage"))
        transactions_btn.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")


# Create Student Page
class CreateStudentPage(ctk.CTkFrame):
    def __init__(self, parent, switch_callback):
        super().__init__(parent)
        self.switch_callback = switch_callback
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        back_btn = ctk.CTkButton(
            self, text="← Back", width=70, height=40,
            command=lambda: switch_callback("FinanceAdminDashboard")
        )
        back_btn.pack(anchor="nw", pady=10, padx=10)

        container = ctk.CTkFrame(self, fg_color="#F0F0F0", corner_radius=15)
        container.pack(padx=50, pady=50, fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            container, text="Create Student Account",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=(20, 40))

        self.student_id_entry = ctk.CTkEntry(
            container, placeholder_text="Enter Student ID",
            width=400, height=40, font=ctk.CTkFont(size=16)
        )
        self.student_id_entry.pack(pady=10)

        review_btn = ctk.CTkButton(
            container, text="View Student Information",
            width=250, height=40, font=ctk.CTkFont(size=16),
            command=self.review_student_info
        )
        review_btn.pack(pady=20)

        self.message_label = ctk.CTkLabel(
            container, text="", font=ctk.CTkFont(size=14), text_color="red"
        )
        self.message_label.pack(pady=10)

    def review_student_info(self):
        student_id = self.student_id_entry.get()
        if not student_id:
            self.message_label.configure(text="Please enter a Student ID.")
            return

        success, student = FinanceAdminWallet.admin_create_student_account(
            student_id, preview_only=True
        )
        if not success:
            self.message_label.configure(text=student)
            return

        message_text = (
            f"Student ID: {student['student_id']}\n"
            f"Name: {student['name']}\n"
            f"Program: {student['program']}\n"
            f"Section: {student['section']}\n"
            f"Email: {student['email']}\n"
            f"Role: {student['role']}\n"
            f"Organization: {student['organization'] or 'N/A'}"
        )

        self.show_confirmation_popup(
            "Confirm Student Account Creation",
            message_text,
            confirm_callback=lambda: self.create_account(student_id)
        )

    def create_account(self, student_id):
        success, result = FinanceAdminWallet.admin_create_student_account(student_id)
        if success:
            self.message_label.configure(text="", text_color="green")
            messagebox.showinfo("Success", result)
            self.student_id_entry.delete(0, "end")
        else:
            self.message_label.configure(text=result, text_color="red")

    def show_confirmation_popup(self, title, message, confirm_callback):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("450x300")
        popup.grab_set()

        frame = ctk.CTkFrame(popup, fg_color="#F0F0F0", corner_radius=15)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10,5))

        scroll_frame = ctk.CTkScrollableFrame(frame, width=400, height=180, corner_radius=10)
        scroll_frame.pack(pady=(5,20), fill="both", expand=True)
        scroll_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            scroll_frame, text=message, font=ctk.CTkFont(size=14),
            wraplength=380, justify="left", anchor="nw"
        ).pack(padx=10, pady=5, anchor="nw")

        btn_frame = ctk.CTkFrame(frame, fg_color="#F0F0F0")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Cancel", width=120, command=popup.destroy).grid(row=0, column=0, padx=10)
        ctk.CTkButton(
            btn_frame, text="Create Account", width=150,
            command=lambda: [confirm_callback(), popup.destroy()]
        ).grid(row=0, column=1, padx=10)


# Cash-In Page
class CashInPage(ctk.CTkFrame):
    def __init__(self, parent, switch_callback):
        super().__init__(parent)
        self.switch_callback = switch_callback

        back_btn = ctk.CTkButton(self, text="←", width=50, height=40,
                                  command=lambda: switch_callback("FinanceAdminDashboard"))
        back_btn.pack(anchor="nw", pady=10, padx=10)

        header = ctk.CTkLabel(self, text="Cash-In Requests", font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(pady=10)

        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=5, fill="x", padx=10)

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(top_frame, placeholder_text="Search...", textvariable=self.search_var)\
            .pack(side="left", fill="x", expand=True)
        ctk.CTkButton(top_frame, text="Search", command=self.load_requests)\
            .pack(side="left", padx=5)

        self.status_var = ctk.StringVar(value="pending")
        self.filter_dropdown = ctk.CTkOptionMenu(
            top_frame,
            variable=self.status_var,
            values=["pending", "approved", "rejected", "all"],
            command=lambda _: self.load_requests()
        )
        self.filter_dropdown.pack(side="left", padx=5)

        self.message_label = ctk.CTkLabel(self, text="Pending Requests", 
                                          font=ctk.CTkFont(size=14, weight="bold"))
        self.message_label.pack(pady=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=950, height=400)
        self.scroll_frame.pack(pady=10)

        self.search_var.trace_add("write", self.on_search_change)
        self.load_requests()

    def on_search_change(self, *args):
        if not self.search_var.get().strip():
            self.load_requests()

    def load_requests(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        search = self.search_var.get()
        filter_status = self.status_var.get()

        success, requests = FinanceAdminWallet.get_all_cashin_requests(
            search=search, 
            status_filter=filter_status
        )

        if search:
            self.message_label.configure(text=f"Results for '{search}'")
        else:
            title = filter_status.capitalize() if filter_status != "all" else "All"
            self.message_label.configure(text=f"{title} Cash-In Requests")

        if not success or len(requests) == 0:
            self.message_label.configure(
                text=f"No result for '{search}'" if search else "No requests found"
            )
            return

        for req in requests:
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#D9FDD3", corner_radius=10)
            card.pack(pady=5, padx=10, fill="x")

            info_label = ctk.CTkLabel(
                card,
                text=f"Request ID: {req['request_id']} | Student: {req['student_id']} "
                     f"| Amount: ₱{req['amount']:.2f} | Status: {req['status']}",
                text_color="#333333",
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            info_label.pack(padx=10, pady=10, fill="x")

            card.bind("<Button-1>", lambda e, r=req: self.switch_callback("CashInDetailPage", r))
            info_label.bind("<Button-1>", lambda e, r=req: self.switch_callback("CashInDetailPage", r))


# Cash-In Detail Page
class CashInDetailPage(ctk.CTkFrame):
    def __init__(self, parent, switch_callback, admin_user_id=None):
        super().__init__(parent)
        self.switch_callback = switch_callback
        self.selected_request = None
        self.admin_user_id = admin_user_id

        back_btn = ctk.CTkButton(self, text="←", width=50, height=40,
                                  command=lambda: switch_callback("CashInPage"))
        back_btn.pack(anchor="nw", pady=10, padx=10)

        header = ctk.CTkLabel(self, text="Cash-In Request Details",
                               font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=10)

        self.card = ctk.CTkFrame(self, fg_color="#D9FDD3", corner_radius=15)
        self.card.pack(pady=20, padx=20, fill="x")

        self.labels = {}
        fields = ["Request ID", "Student ID", "Student Name", "Amount", "Status", "Date Requested"]
        for field in fields:
            lbl = ctk.CTkLabel(self.card, text="", anchor="w", text_color="#333333",
                               font=ctk.CTkFont(size=14))
            lbl.pack(padx=10, pady=5, fill="x")
            self.labels[field] = lbl

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        self.approve_btn = ctk.CTkButton(btn_frame, text="Approve", command=self.approve_request)
        self.approve_btn.grid(row=0, column=0, padx=20)
        self.decline_btn = ctk.CTkButton(btn_frame, text="Decline", command=self.decline_request)
        self.decline_btn.grid(row=0, column=1, padx=20)

    def load_data(self, request):
        self.selected_request = request
        self.labels["Request ID"].configure(text=f"Request ID: {request['request_id']}")
        self.labels["Student ID"].configure(text=f"Student ID: {request['student_id']}")
        self.labels["Student Name"].configure(text=f"Student Name: {request['student_name']}")
        self.labels["Amount"].configure(text=f"Amount: ₱{request['amount']:.2f}")
        self.labels["Status"].configure(text=f"Status: {request['status']}")
        self.labels["Date Requested"].configure(text=f"Date Requested: {request['date_requested']}")

        if request["status"] != "pending":
            self.approve_btn.configure(state="disabled")
            self.decline_btn.configure(state="disabled")
        else:
            self.approve_btn.configure(state="normal")
            self.decline_btn.configure(state="normal")

    def approve_request(self):
        if self.selected_request and messagebox.askyesno("Confirm", "Approve this cash-in request?"):
            success, msg = FinanceAdminWallet.approve_cashin_request(
                self.selected_request['request_id'],
                self.admin_user_id
            )
            messagebox.showinfo("Result", msg)
            self.switch_callback("CashInPage")

    def decline_request(self):
        if self.selected_request:
            reason = simpledialog.askstring("Decline Reason", "Enter reason for declining:")
            if not reason:
                return
            if messagebox.askyesno("Confirm", "Decline this cash-in request?"):
                success, msg = FinanceAdminWallet.decline_cashin_request(self.selected_request['request_id'], reason)
                messagebox.showinfo("Result", msg)
                self.switch_callback("CashInPage")


# Cash-Out Page
class CashOutPage(ctk.CTkFrame):
    def __init__(self, parent, switch_callback, admin_user_id=None):
        super().__init__(parent)
        self.switch_callback = switch_callback
        self.admin_user_id = admin_user_id

        back_btn = ctk.CTkButton(self, text="←", width=50, height=40,
                                  command=lambda: switch_callback("FinanceAdminDashboard"))
        back_btn.pack(anchor="nw", pady=10, padx=10)

        header = ctk.CTkLabel(self, text="Cash-Out Requests", font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(pady=10)

        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=5, fill="x", padx=10)

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(top_frame, placeholder_text="Search...", textvariable=self.search_var).pack(
            side="left", fill="x", expand=True
        )
        ctk.CTkButton(top_frame, text="Search", command=self.load_requests).pack(side="left", padx=5)

        self.filter_var = ctk.StringVar(value="pending")
        self.filter_menu = ctk.CTkOptionMenu(
            top_frame,
            values=["pending", "approved", "declined", "all"],
            variable=self.filter_var,
            command=lambda _: self.load_requests()
        )
        self.filter_menu.pack(side="left", padx=5)

        self.message_label = ctk.CTkLabel(self, text="Pending Cash-Out Requests",
                                          font=ctk.CTkFont(size=14, weight="bold"))
        self.message_label.pack(pady=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=950, height=400)
        self.scroll_frame.pack(pady=10)

        self.search_var.trace_add("write", self.on_search_change)
        self.load_requests()

    def on_search_change(self, *args):
        if not self.search_var.get().strip():
            self.load_requests()

    def load_requests(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        search = self.search_var.get()
        status_filter = self.filter_var.get()

        success, requests = FinanceAdminWallet.get_all_cashout_requests(
            search=search,
            status_filter=status_filter
        )

        status_text = {
            "pending": "Pending Cash-Out Requests",
            "approved": "Approved Cash-Out Requests",
            "declined": "Declined Cash-Out Requests",
            "all": "All Cash-Out Requests"
        }
        self.message_label.configure(text=status_text.get(status_filter, "Cash-Out Requests"))

        if not success or len(requests) == 0:
            self.message_label.configure(
                text=f"No results found for '{search}'" if search else "No cash out requests"
            )
            return

        for req in requests:
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#FFD9D9", corner_radius=10)
            card.pack(pady=5, padx=10, fill="x")

            requester_name = req.get("organization_name") if req.get("org_wallet_id") else req.get("service_name")
            info_label = ctk.CTkLabel(
                card,
                text=f"Request ID: {req['request_id']} | Requester: {requester_name} | Amount: ₱{req['amount']:.2f}",
                text_color="#333333",
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            info_label.pack(padx=10, pady=10, fill="x")

            # Always clickable (CashOutDetailPage will disable buttons if not pending)
            card.bind("<Button-1>", lambda e, r=req: self.switch_callback("CashOutDetailPage", r))
            info_label.bind("<Button-1>", lambda e, r=req: self.switch_callback("CashOutDetailPage", r))


# Cash-Out Detail Page
class CashOutDetailPage(ctk.CTkFrame):
    def __init__(self, parent, switch_callback, admin_user_id=None):
        super().__init__(parent)
        self.switch_callback = switch_callback
        self.admin_user_id = admin_user_id
        self.selected_request = None

        back_btn = ctk.CTkButton(self, text="←", width=50, height=40,
                                  command=lambda: switch_callback("CashOutPage"))
        back_btn.pack(anchor="nw", pady=10, padx=10)

        header = ctk.CTkLabel(self, text="Cash-Out Request Details",
                               font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=10)

        self.card = ctk.CTkFrame(self, fg_color="#FFD9D9", corner_radius=15)
        self.card.pack(pady=20, padx=20, fill="x")

        self.labels = {}
        fields = ["Request ID", "Requester", "Treasurer", "Amount", "Status", "Date Requested", "Message"]
        for field in fields:
            lbl = ctk.CTkLabel(self.card, text="", anchor="w", text_color="#333333",
                               font=ctk.CTkFont(size=14))
            lbl.pack(padx=10, pady=5, fill="x")
            self.labels[field] = lbl

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        self.approve_btn = ctk.CTkButton(btn_frame, text="Approve", state="disabled", command=self.approve_request)
        self.approve_btn.grid(row=0, column=0, padx=20)
        self.decline_btn = ctk.CTkButton(btn_frame, text="Decline", state="disabled", command=self.decline_request)
        self.decline_btn.grid(row=0, column=1, padx=20)

    def load_data(self, request):
        self.selected_request = request

        requester_name = request.get("organization_name") if request.get("org_wallet_id") else request.get("service_name")
        treasurer_name = request.get("treasurer_name", "N/A") if request.get("org_wallet_id") else "N/A"
        treasurer_id = request.get("treasurer_id", "") if request.get("org_wallet_id") else ""

        self.labels["Request ID"].configure(text=f"Request ID: {request['request_id']}")
        self.labels["Requester"].configure(text=f"Requester: {requester_name}")
        self.labels["Treasurer"].configure(text=f"Treasurer: {treasurer_name} ({treasurer_id})")
        self.labels["Amount"].configure(text=f"Amount: ₱{request['amount']:.2f}")
        self.labels["Status"].configure(text=f"Status: {request['status']}")
        self.labels["Date Requested"].configure(text=f"Date Requested: {request['date_requested']}")
        self.labels["Message"].configure(text=f"Message: {request.get('message','')}")

        if request.get("status") == "pending":
            self.approve_btn.configure(state="normal")
            self.decline_btn.configure(state="normal")
        else:
            self.approve_btn.configure(state="disabled")
            self.decline_btn.configure(state="disabled")

    def approve_request(self):
        if self.selected_request and messagebox.askyesno("Confirm", "Approve this cash-out request?"):
            success, msg = FinanceAdminWallet.approve_cashout_request(
                self.selected_request['request_id'],
                self.admin_user_id
            )
            messagebox.showinfo("Result", msg)
            self.switch_callback("CashOutPage")

    def decline_request(self):
        if self.selected_request:
            reason = simpledialog.askstring("Decline Reason", "Enter reason for declining:")
            if not reason:
                return
            if messagebox.askyesno("Confirm", "Decline this cash-out request?"):
                success, msg = FinanceAdminWallet.decline_cashout_request(
                    self.selected_request['request_id'],
                    reason
                )
                messagebox.showinfo("Result", msg)
                self.switch_callback("CashOutPage")


# Transactions Page
class TransactionsPage(ctk.CTkFrame):
    def __init__(self, parent, switch_callback):
        super().__init__(parent)
        self.switch_callback = switch_callback

        back_btn = ctk.CTkButton(self, text="←", width=50, height=40,
                                  command=lambda: switch_callback("FinanceAdminDashboard"))
        back_btn.pack(anchor="nw", pady=10, padx=10)

        header = ctk.CTkLabel(self, text="Transactions", font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(pady=10)

        self.search_var = ctk.StringVar()
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(pady=5, fill="x", padx=10)
        ctk.CTkEntry(search_frame, placeholder_text="Search...", textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(search_frame, text="Search", command=self.load_transactions).pack(side="left", padx=5)

        self.message_label = ctk.CTkLabel(self, text="All Transactions", font=ctk.CTkFont(size=14, weight="bold"))
        self.message_label.pack(pady=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=950, height=400)
        self.scroll_frame.pack(pady=10)

        self.search_var.trace_add("write", self.on_search_change)
        self.load_transactions()

    def on_search_change(self, *args):
        if not self.search_var.get():
            self.message_label.configure(text="All Transactions")

    def load_transactions(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        search = self.search_var.get()
        success, transactions = FinanceAdminWallet.get_all_transactions(search=search)
        if search:
            self.message_label.configure(text=f"Results for '{search}'")
        else:
            self.message_label.configure(text="All Transactions")

        if not success or len(transactions) == 0:
            self.message_label.configure(text=f"No results found for '{search}'" if search else "No transactions")
            return

        for txn in transactions:
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#E6F4EA", corner_radius=10)
            card.pack(pady=5, padx=10, fill="x")

            txn_type = txn.get('transaction_type', 'Unknown')
            student_id = txn.get('student_id', 'N/A')
            amount = txn.get('amount', 0.0)
            status = txn.get('status', 'N/A')

            info_label = ctk.CTkLabel(
                card,
                text=f"{txn_type.capitalize()} | Student: {student_id} | Amount: ₱{amount:.2f} | Status: {status}",
                text_color="#333333",
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            info_label.pack(padx=10, pady=10, fill="x")


if __name__ == "__main__":
    app = App()
    app.mainloop()