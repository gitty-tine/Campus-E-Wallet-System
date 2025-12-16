import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
class StudentDashboard(ctk.CTkToplevel):
    def __init__(self, wallet_backend, user_data):
        super().__init__()
        self.title("Student Dashboard") 
        self.geometry("1366x768") 
        self.resizable(True, True)
        self.wallet_backend = wallet_backend
        self.backend = wallet_backend
        self.student_wallet = wallet_backend
        self.user_data = user_data

        # Main Layout 
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=(12, 20))

        # Top bar for Welcome and Logout 
        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 20))

        # Welcome Label
        welcome_label = ctk.CTkLabel(
            top_bar,
            height=44,
            text="Welcome, Student",
            font=("Times New Roman", 40)
        )
        welcome_label.pack(side="left", padx=5)

        # Logout Button
        logout_btn = ctk.CTkButton(
            top_bar,
            text="Logout",
            width=120,
            command=self.logout
        )
        logout_btn.pack(side="right", padx=5, pady=10)

        # Student Wallet Header
        student_wallet_label = ctk.CTkLabel(
            self.main_frame,
            height=60,
            text="Student Wallet",
            font=("Times New Roman", 16),
            fg_color="#A8D9A4",
            corner_radius=10
        )
        student_wallet_label.pack(fill="x", pady=5)

        # Balance Label
        balance = self.student_wallet.get_balance() or 0.0
        self.update_balance = ctk.CTkLabel(
            self.main_frame,
            height=70,
            text=f"₱ {balance:.2f}",
            fg_color="#8fc98f",
            corner_radius=20,
            font=("Times New Roman", 30, "bold")
        )
        self.update_balance.pack(fill="x", pady=5)
        self._update_balance_display() # Initial balance update

        # Dynamic Content Frame 
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Load the main services view initially
        self.show_main_services()

    def logout(self):
        """Destroys the dashboard window to return to the login screen."""
        self.destroy()

    # Method to update the balance display
    def _update_balance_display(self):
        balance = self.student_wallet.get_balance() or 0.0
        self.update_balance.configure(text=f"₱ {balance:.2f}")

    # Clear content frame 
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # Main Services View 
    def show_main_services(self):
        self.clear_content_frame()

        # Services Title
        services_title = ctk.CTkLabel(
            self.content_frame,
            text="List of Services",
            font=("Times New Roman", 22, "bold")
        )
        services_title.pack(anchor="center", pady=(15, 5))

        # Services Container
        services_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        services_container.pack(anchor="center", pady=(15, 0))

        # Service Cards
        self.create_service_card(services_container, "💸", "Send Money", self.send_money_frame)
        self.create_service_card(services_container, "📝", "Request Funds", self.request_funds_frame)
        self.create_service_card(services_container, "🏫", "View Cash-In Request", self.show_cash_in_frame)
        self.create_service_card(services_container, "📄", "View Post Bills", self.show_post_bills_frame)
        self.create_service_card(services_container, "📄", "View Transaction", self.show_transaction_history)

    # Service Card Helper 
    def create_service_card(self, parent, emoji, text, command):
        card = ctk.CTkFrame(parent, width=180, height=180, fg_color="transparent")
        card.pack_propagate(False)
        card.pack(side="left", padx=8) 

        ctk.CTkButton(
            card,
            text=emoji,
            width=100,
            height=100,
            fg_color="#B7E5B9",
            font=("Times New Roman", 50, "bold"),
            command=command
        ).pack(pady=(8, 4))

        ctk.CTkLabel(card, text=text, font=("Times New Roman", 15, "bold", "italic")).pack(anchor="center")

    # Send Money Frame 1
    def send_money_frame(self):
        self.clear_content_frame()

        # Title
        send_money_title_label = ctk.CTkLabel(self.content_frame, text="Send Money", font=("Times New Roman", 25, "bold"))
        send_money_title_label.pack(pady=30)

        # ID Entry
        send_money_id_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Enter Recipient ID", width=350, corner_radius=10, height=45)
        send_money_id_entry.pack(pady=15)

        # Amount Entry
        send_money_amount_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Enter Amount", width=350, corner_radius=10, height=45)
        send_money_amount_entry.pack(pady=15)

        # Send Money Button
        send_money_btn = ctk.CTkButton(self.content_frame, text="Send Money", width=350, height=50, fg_color="#4CAF50", hover_color="#43A047", corner_radius=10,
                                        command=lambda: self.sending_money(send_money_id_entry.get(), send_money_amount_entry.get()))
        send_money_btn.pack(pady=30)

        # Back Button
        back_btn = ctk.CTkButton(self.content_frame, text="Back", width=150, height=45, fg_color="#A8D9A4", corner_radius=10, command=self.show_main_services)
        back_btn.pack(pady=10)


    # Send Money Frame 2
    def sending_money(self, recipient_id, amount):
        try:
            amount = float(amount)
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid amount entered.", icon="error")
            return

        result = self.backend.send_money(recipient_id, amount) 
        ok, msg = result # unpack tuple 
        if ok: 
            CTkMessagebox(title="Success", message="Money sent successfully!", icon="info")
            self._update_balance_display() # Update balance after successful send
            self.show_main_services() # Navigate back to main services
        else: 
            CTkMessagebox(title="Error", message=msg, icon="error")
 
    # Request Funds Frame 2
    def request_funds_frame(self):
        self.clear_content_frame()

        # Title
        cash_in_title_label = ctk.CTkLabel(self.content_frame, text="Request Cash-In", font=("Times New Roman", 25, "bold"))
        cash_in_title_label.pack(pady=30)

        # Amount Entry
        cash_in_amount_entry = ctk.CTkEntry( self.content_frame, placeholder_text="Enter Amount", corner_radius=10, width=350, height=45)
        cash_in_amount_entry.pack(pady=15)

        # Request Funds Button
        cash_in_request_btn = ctk.CTkButton( self.content_frame, text="Request Funds", width=350, height=50, fg_color="#2196F3", hover_color="#1E88E5", corner_radius=10,
                                             command=lambda: self.request_funds_handler(cash_in_amount_entry.get()))
        cash_in_request_btn.pack(pady=30)

        # Back Button
        cash_in_back_btn = ctk.CTkButton(self.content_frame, text="Back", width=150, height=45, fg_color="#A8D9A4", corner_radius=10, command=self.show_main_services)
        cash_in_back_btn.pack(pady=10)

    # Request Funds Frame 2
    def request_funds_handler(self, amount_entry):

        ok, result = self.backend.request_funds(amount_entry)

        if ok:
            # result is a dict with request_id, user_id, amount, status
            CTkMessagebox(
                title="Success",
                message=f"Funds request submitted!\nRequest ID: {result['request_id']}\nAmount: {result['amount']}",
                icon="info"
            )
            self._update_balance_display() # Update balance
            self.show_main_services() # Go back to main student services
        else:
            # result is an error message string
            CTkMessagebox(
                title="Error",
                message=result,
                icon="error"
            )

    # View Cash In Frame
    def show_cash_in_frame(self):
        self.clear_content_frame()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Cash-In Requests",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=15)

        # Status Filter
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        filter_frame.pack(pady=5)

        self.cashin_status = ctk.StringVar(value="Pending")

        for status in ["Pending", "Successful", "Failed"]:
            ctk.CTkRadioButton(
                filter_frame,
                text=status,
                value=status,
                variable=self.cashin_status,
                command=self.refresh_cashin_list
            ).pack(side="left", padx=15)

        # Scrollable list container
        self.cashin_list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=700
        )
        self.cashin_list_frame.pack(pady=10, fill="x", expand=True) 

        # Footer frame for Back button
        footer_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        footer_frame.pack(pady=10)

        ctk.CTkButton(
            footer_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=self.show_main_services
        ).pack()

        self.refresh_cashin_list()


    def view_cashin_requests_handler(self, search_id, status_filter, results_frame):
        # Clear old results
        for widget in results_frame.winfo_children():
            widget.destroy()

        try:
            rows = self.backend.view_cashin_requests(search_id=search_id, status_filter=status_filter)

            if not rows:
                ctk.CTkLabel(results_frame, text="No requests found.", font=("Times New Roman", 14)).pack(pady=10)
                return

            # Table headers
            header = ctk.CTkFrame(results_frame)
            header.pack(fill="x", pady=5)
            for col in ["Request ID", "Amount", "Status", "Date"]:
                ctk.CTkLabel(header, text=col, font=("Times New Roman", 14, "bold"), width=120).pack(side="left", padx=5)

            # Table rows
            for req_id, amount, status, date_requested in rows:
                row_frame = ctk.CTkFrame(results_frame)
                row_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(row_frame, text=req_id, width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=f"{amount:.2f}", width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=status, width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=str(date_requested), width=120).pack(side="left", padx=5)

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to load requests: {e}", icon="error")

    # Status for Cash In
    def refresh_cashin_list(self):
        for widget in self.cashin_list_frame.winfo_children():
            widget.destroy()

        status_map = {
            "Pending": "pending",
            "Successful": "success",   
            "Failed": "failed"
        }
        status = status_map.get(self.cashin_status.get())

        try:
            rows = self.backend.view_cashin_requests(status_filter=status)
            print("Rows returned:", rows)  

            requests = rows
        except Exception as e:
            ctk.CTkLabel(self.cashin_list_frame, text=f"Error loading requests: {e}", text_color="red").pack(pady=20)
            return

        if not requests:
            ctk.CTkLabel(self.cashin_list_frame, text="No cash-in requests found.", text_color="gray").pack(pady=20)
            return

        for i, req in enumerate(requests):
            bg_color = "#F9F9F9" if i % 2 == 0 else "white"
            card = ctk.CTkFrame(self.cashin_list_frame, corner_radius=8, fg_color=bg_color)
            card.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(card, text=f"Request ID: {req['request_id']}", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card, text=f"Amount: ₱{float(req['amount']):.2f}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Status: {req['status']}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Date: {req['date_requested']}", text_color="gray").pack(anchor="w", padx=10, pady=2)

            if req['status'].lower() == "pending":
                ctk.CTkButton(card, text="Cancel", width=100, height=30,
                            fg_color="#E57373", hover_color="#C62828",
                            command=lambda rid=req['request_id']: self.cancel_request(rid)).pack(anchor="e", padx=10, pady=5)


    def show_post_bills_frame(self):
        self.clear_content_frame()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Posted Bills",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=15)

        # Search Bar 
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(pady=5)

        self.bill_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search Bill ID",
            width=250
        )
        self.bill_search_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=self.refresh_posted_bills
        ).pack(side="left", padx=5)

        # Scrollable Bills List 
        self.posted_bills_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=750
        )
        self.posted_bills_frame.pack(pady=10, fill="both", expand=True) 
 
        # Footer (Back button)
        footer = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        footer.pack(pady=10)

        ctk.CTkButton(
            footer,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=self.show_main_services
        ).pack()

        self.refresh_posted_bills()

    # Post Bill Frame
    def load_organization_posts_handler(self, results_frame):
        for widget in results_frame.winfo_children():
            widget.destroy()

        try:
            rows = self.backend.load_organization_posts()

            if not rows:
                ctk.CTkLabel(results_frame, text="No organization posts found.", text_color="gray").pack(pady=20)
                return

            # Build cards for each post
            for i, row in enumerate(rows):
                bill_id, title, description, amount, org_name = row

                bg_color = "#F9F9F9" if i % 2 == 0 else "white"
                card = ctk.CTkFrame(results_frame, corner_radius=8, fg_color=bg_color)
                card.pack(fill="x", padx=10, pady=8)

                ctk.CTkLabel(card, text=f"{title}", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=2)
                ctk.CTkLabel(card, text=f"Organization: {org_name}", font=("Arial", 12)).pack(anchor="w", padx=10)
                ctk.CTkLabel(card, text=f"Amount: ₱{float(amount):.2f}", font=("Arial", 12)).pack(anchor="w", padx=10)
                ctk.CTkLabel(card, text=f"Description: {description}", font=("Arial", 11), wraplength=650).pack(anchor="w", padx=10, pady=2)
                ctk.CTkLabel(card, text=f"Bill ID: {bill_id}", text_color="gray", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)

        except Exception as e:
            ctk.CTkLabel(results_frame, text=f"Error loading posts: {e}", text_color="red").pack(pady=20)

    def refresh_posted_bills(self):
        for widget in self.posted_bills_frame.winfo_children():
            widget.destroy()

        search_value = self.bill_search_entry.get().strip()
        bills = self.wallet_backend.view_posted_bills(search_value if search_value else None)

        if not bills:
            ctk.CTkLabel(
                self.posted_bills_frame,
                text="No posted bills found.",
                text_color="gray"
            ).pack(pady=20)
            return

        # Build cards for each bill
        for i, bill in enumerate(bills):
            bg_color = "#F9F9F9" if i % 2 == 0 else "white"
            card = ctk.CTkFrame(self.posted_bills_frame, corner_radius=10, fg_color=bg_color)
            card.pack(fill="x", padx=10, pady=8)

            # Bill Info
            ctk.CTkLabel(
                card,
                text=f"{bill['title']}",
                font=("Arial", 14, "bold")
            ).pack(anchor="w", padx=10, pady=2)

            ctk.CTkLabel(
                card,
                text=f"Organization: {bill.get('organization_name', 'N/A')}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Amount: ₱{float(bill['amount']):.2f}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Description: {bill['description']}",
                font=("Arial", 11),
                wraplength=650
            ).pack(anchor="w", padx=10, pady=2)

            ctk.CTkLabel(
                card,
                text=f"Bill ID: {bill['bill_id']}",
                text_color="gray",
                font=("Arial", 10)
            ).pack(anchor="w", padx=10, pady=2)

            # Pay Button
            ctk.CTkButton(
                card,
                text="Pay",
                width=120,
                fg_color="#4CAF50",
                hover_color="#43A047",
                command=lambda b_id=bill['bill_id']: self.pay_bill_handler(b_id)
            ).pack(anchor="e", padx=10, pady=8)

    # Pay Post Bill
    def pay_bill_handler(self, bill_id, message_entry=None):
        message = None
        if message_entry:
            message = message_entry.get("0.0", "end").strip()

        ok, result = self.backend.pay_organization_bill(bill_id, message)

        if ok:
            CTkMessagebox(
                title="Success",
                message=(
                    f"Bill paid successfully!\n"
                    f"Transaction ID: {result['transaction_id']}\n"
                    f"Organization: {result['organization']}\n"
                    f"Amount: ₱{result['amount']:.2f}"
                ),
                icon="info"
            )
            self._update_balance_display() # Update balance
            self.refresh_posted_bills() # Refresh the list of bills
        else:
            CTkMessagebox(
                title="Error",
                message=result,  
                icon="cancel"
            )

    def show_transaction_history(self):
        self.clear_content_frame() 

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Transaction History",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=15)

        # Container for scrollable frame
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Scrollable frame for transactions
        scroll_frame = ctk.CTkScrollableFrame(container)
        scroll_frame.pack(fill="both", expand=True, side="top", pady=(0, 10))

        # Call handler to populate transactions
        self.view_transactions_handler(scroll_frame)

        # Back Button pinned at bottom 
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="⬅ Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=self.show_main_services  # call main dashboard
        )
        back_btn.pack(side="bottom", pady=10)


    def view_transactions_handler(self, results_frame):
        # Clear old results
        for widget in results_frame.winfo_children():
            widget.destroy()

        try:
            rows = self.backend.view_transactions()

            if not rows:
                ctk.CTkLabel(results_frame, text="No transactions found.", text_color="gray").pack(pady=20)
                return

            # Table headers
            header = ctk.CTkFrame(results_frame)
            header.pack(fill="x", pady=5, padx=10)
            headers = ["Date", "Direction", "Sender", "Receiver", "Amount", "Type", "Status"]
            for col_text in headers:
                ctk.CTkLabel(header, text=col_text, font=("Times New Roman", 14, "bold"), width=120, anchor="w").pack(side="left", padx=5, expand=True)

            # Table rows
            for row in rows:
                row_frame = ctk.CTkFrame(results_frame)
                row_frame.pack(fill="x", pady=2, padx=10)
                ctk.CTkLabel(row_frame, text=str(row.get('created_at', 'N/A')), width=120, anchor="w").pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(row_frame, text=row.get('direction', 'N/A'), width=120, anchor="w").pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(row_frame, text=row.get('sender_name', 'N/A'), width=120, anchor="w").pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(row_frame, text=row.get('receiver_name', 'N/A'), width=120, anchor="w").pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(row_frame, text=f"₱{float(row.get('amount', 0)):.2f}", width=120, anchor="w").pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(row_frame, text=row.get('transaction_type', 'N/A'), width=120, anchor="w").pack(side="left", padx=5, expand=True)
                ctk.CTkLabel(row_frame, text=row.get('status', 'N/A'), width=120, anchor="w").pack(side="left", padx=5, expand=True)

        except Exception as e:
            ctk.CTkLabel(results_frame, text=f"Error loading transactions: {e}", text_color="red").pack(pady=20)

    def show_service_frame(self, title):
        self.clear_content_frame()

        # Service title
        label = ctk.CTkLabel(self.content_frame, text=title, font=("Times New Roman", 25, "bold"))
        label.pack(pady=50)

        # Back Button
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="Back",
            height=50,
            width=150,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=self.show_main_services
        )
        back_btn.pack(pady=20)


import system_backend.organization_wallet
class StudentOrganizationDashboard(ctk.CTkToplevel):
    def __init__(self, student_wallet_backend, user_data, organization_wallet_backend=None):
        super().__init__()
        self.title("Dashboard") 
        self.geometry("1366x768") 
        self.resizable(True, True)
        self.student_backend = student_wallet_backend
        self.organization_backend = organization_wallet_backend
        self.user_data = user_data
        self.current_wallet_type = "student"
        self.frontend = self

        print(f"wallet_backend: {self.student_backend}")
        print(f"organization_wallet: {self.organization_backend}")
        print(f"self.frontend: {self.frontend}")
        print(f"Has post_bill: {hasattr(self.frontend, 'post_bill') if self.frontend else False}")
       # Top static wallet frame 
        self.wallet_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.wallet_frame.pack(fill="x", pady=(10, 0), padx=40)

        # Welcome
        welcome_label = ctk.CTkLabel(
            self.wallet_frame,
            text="Welcome, Student",
            font=("Times New Roman", 40)
        )
        welcome_label.pack(anchor="w", padx=5, pady=(20, 10))

            # Buttons container (Side by Side)
        buttons_frame = ctk.CTkFrame(self.wallet_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 10))

        self.student_wallet_btn = ctk.CTkButton(
            buttons_frame,
            text="Student Wallet",
            height=60,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("student")
        )
        self.student_wallet_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.org_wallet_btn = ctk.CTkButton(
            buttons_frame,
            text="Organization Wallet",
            height=60,
            fg_color="#FFD580",
            corner_radius=10,
            command=lambda: self.show_content("organization")
        )
        self.org_wallet_btn.pack(side="left", expand=True, fill="x", padx=(8, 0))


        # Balance Label (below buttons) 
        self.balance_display_label = ctk.CTkLabel(
            self.wallet_frame,
            height=60,
            text="",
            fg_color="#8fc98f",
            corner_radius=20,
            font=("Times New Roman", 30, "bold")
        )
        self.balance_display_label.pack(fill="x", pady=(10, 15))

 
        # Dynamic content frame 
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Start with Student Wallet content
        self.show_content("student")

        # Logout Button
        logout_btn = ctk.CTkButton(
            self.wallet_frame,
            text="Logout",
            command=self.logout
        )
        logout_btn.place(relx=0.98, rely=0.1, anchor="ne")

    # Method to update the balance display
    def _update_balance_display(self, wallet_type):
        balance = 0.0
        if wallet_type == "student":
            balance = self.student_backend.get_balance()
            self.balance_display_label.configure(fg_color="#8fc98f")
        elif wallet_type == "organization":
            balance = self.organization_backend.get_balance()
            self.balance_display_label.configure(fg_color="#FFD580") 

        if balance is not None:
            self.balance_display_label.configure(text=f"₱{balance:,.2f}")
        else:
            self.balance_display_label.configure(text="No Wallet Found")

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def logout(self):
        """Destroys the dashboard window to return to the login screen."""
        self.destroy()

    def show_content(self, wallet_type):
        self.current_wallet_type = wallet_type
        self.clear_content_frame()

        # Update the balance display based on the selected wallet type
        self._update_balance_display(wallet_type)

        # Services Title
        title_text = "List of Services" if wallet_type == "student" else "Organization Services"
        ctk.CTkLabel(
            self.content_frame,
            text=title_text,
            font=("Times New Roman", 22, "bold")
        ).pack(anchor="center", pady=(15,5))

        # Services Container
        services_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        services_container.pack(anchor="center", pady=(15,0))

        # Service Cards
        if wallet_type == "student":
            self.create_service_card(services_container, "💸", "Send Money", "send_money")
            self.create_service_card(services_container, "📝", "Request Funds", "request_funds")
            self.create_service_card(services_container, "🏫", "View Cash-In Request", "view_cash_in")
            self.create_service_card(services_container, "📄", "View Post Bills", "view_post_bills")
            self.create_service_card(services_container, "📄", "View Transaction","view_transaction" )
        else:
            self.create_service_card(services_container, "💸", "Post Bill", "post_bill")
            self.create_service_card(services_container, "📝", "Request Cash Out", "request_cash_out")
            self.create_service_card(services_container, "🏫", "View Request", "view_request")
            self.create_service_card(services_container, "📄", "View Organzation Transaction", "view_org_transaction")

    def create_service_card(self, parent, emoji, text, key):
        card = ctk.CTkFrame(parent, width=120, height=160, fg_color="transparent") 
        card.pack_propagate(False)
        card.pack(side="left", padx= 50) 

        # Special handling for Personal Wallet
        if key == "send_money":
            command = self.stu_send_money_frame

        elif key == "request_funds":
            command = self.stu_request_funds_frame
        
        elif key == "view_cash_in":
            command = self.stu_show_cash_in_frame

        elif key == "view_post_bills":
            command = self.show_post_bills_frame

        elif key == "view_transaction":
            command = self.stu_show_transaction_history

        # Special handling for Organization Wallet
        elif key == "post_bill":
            command = self.org_post_bill_frame

        elif key == "request_cash_out":
            command = self.org_request_cash_out_frame
        
        elif key == "view_request":
            command = self.org_view_cash_out_requests_frame
        
        elif key =="view_org_transaction":
            command = self.org_view_transactions_frame
        else:
            command = lambda: print(f"{key} clicked")  

        ctk.CTkButton(
            card,
            text=emoji,
            width=100,
            height=100,
            fg_color="#B7E5B9",
            font=("Times New Roman", 50, "bold"),
            command=command
        ).pack(pady=(8,4))

        ctk.CTkLabel(
            card,
            text=text,
            font=("Times New Roman", 15, "bold", "italic")
        ).pack(anchor="center")

    def stu_send_money_frame(self):
        self.clear_content_frame()

        # Title
        send_money_title_label = ctk.CTkLabel(
            self.content_frame,
            text="Send Money",
            font=("Times New Roman", 25, "bold")
        )
        send_money_title_label.pack(pady=20)

        # Recipient ID Entry
        self.send_money_id_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Enter Recipient ID",
            width=350,
            corner_radius=10,
            height=45
        )
        self.send_money_id_entry.pack(pady=10)

        # Amount Entry
        self.send_money_amount_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Enter Amount",
            width=350,
            corner_radius=10,
            height=45
        )
        self.send_money_amount_entry.pack(pady=10)

        # Send Money Button
        send_money_btn = ctk.CTkButton(
            self.content_frame,
            text="Send Money",
            width=350,
            height=50,
            fg_color="#4CAF50",
            hover_color="#43A047",
            corner_radius=10,
            command=lambda: self.student_send_money(
                self.send_money_id_entry.get(),
                self.send_money_amount_entry.get()
            )
        )
        send_money_btn.pack(pady=20)

        # Back Button
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("student")  
        )
        back_btn.pack(pady=10)
 
    def student_send_money(self, recipient_id, amount):
        try:
            amount = float(amount)
        except ValueError:
            CTkMessagebox(title="Error", message="Invalid amount entered.", icon="error")
            return

        result = self.student_backend.send_money(recipient_id, amount) 
        ok, msg = result 
        if ok: 
            CTkMessagebox(title="Success", message="Money sent successfully!", icon="info")
            self._update_balance_display() 
            self.show_content("student") 

        else: 
            CTkMessagebox(title="Error", message=msg, icon="error")
 
    def stu_request_funds_frame(self):
        self.clear_content_frame()

        # Title
        cash_in_title_label = ctk.CTkLabel(
            self.content_frame,
            text="Request Cash-In",
            font=("Times New Roman", 25, "bold")
        )
        cash_in_title_label.pack(pady=30)

        # Amount Entry
        cash_in_amount_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Enter Amount",
            corner_radius=10,
            width=350,
            height=45
        )
        cash_in_amount_entry.pack(pady=15)

        # Request Funds Button
        cash_in_request_btn = ctk.CTkButton(self.content_frame, text="Request Funds", width=350, height=50, 
                                            fg_color="#2196F3", hover_color="#1E88E5", corner_radius=10,
                                            command=lambda: self.request_funds_handler(cash_in_amount_entry.get()))
        cash_in_request_btn.pack(pady=30)

        # Back Button
        cash_in_back_btn = ctk.CTkButton(
            self.content_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("student")  
        )
        cash_in_back_btn.pack(pady=10)

    def request_funds_handler(self, amount_entry):
        ok, result = self.student_backend.request_funds(amount_entry)

        if ok:
            # result is a dict with request_id, user_id, amount, status
            CTkMessagebox(
                title="Success",
                message=f"Funds request submitted!\nRequest ID: {result['request_id']}\nAmount: {result['amount']}",
                icon="info"
            )
            self._update_balance_display() 
            self.show_content("student") 
        else:
            # result is an error message string
            CTkMessagebox(
                title="Error",
                message=result,
                icon="error"
            )

    def stu_show_cash_in_frame(self):
        self.clear_content_frame()
        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Cash-In Requests",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=15)

        # Status Filter
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        filter_frame.pack(pady=5)

        self.cashin_status = ctk.StringVar(value="Pending")

        for status in ["Pending", "Successful", "Failed"]:
            ctk.CTkRadioButton(
                filter_frame,
                text=status,
                value=status,
                variable=self.cashin_status,
                command=self.refresh_cashin_list  
            ).pack(side="left", padx=15)

        # Scrollable list container
        self.cashin_list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=700
        )
        self.cashin_list_frame.pack(pady=(5,50), fill="x", expand=True) 
 
        # Footer frame for Back button
        footer_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        footer_frame.pack(pady=(5, 30))

        ctk.CTkButton(
            footer_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("student")  
        ).pack()

        self.refresh_cashin_list()  
 
    def view_cashin_requests_handler(self, search_id, status_filter, results_frame):
        # Clear old results
        for widget in results_frame.winfo_children():
            widget.destroy()

        try:
            rows = self.student_backend.view_cashin_requests(search_id=search_id, status_filter=status_filter)

            if not rows:
                ctk.CTkLabel(results_frame, text="No requests found.", font=("Times New Roman", 14)).pack(pady=10)
                return

            # Table headers
            header = ctk.CTkFrame(results_frame)
            header.pack(fill="x", pady=5)
            for col in ["Request ID", "Amount", "Status", "Date"]:
                ctk.CTkLabel(header, text=col, font=("Times New Roman", 14, "bold"), width=120).pack(side="left", padx=5)

            # Table rows
            for req_id, amount, status, date_requested in rows:
                row_frame = ctk.CTkFrame(results_frame)
                row_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(row_frame, text=req_id, width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=f"{amount:.2f}", width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=status, width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row_frame, text=str(date_requested), width=120).pack(side="left", padx=5)

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to load requests: {e}", icon="error")

    def refresh_cashin_list(self):
        for widget in self.cashin_list_frame.winfo_children():
            widget.destroy()

        status_map = {
            "Pending": "pending",
            "Successful": "success",   
            "Failed": "failed"
        }
        status = status_map.get(self.cashin_status.get())

        try:
            rows = self.student_backend.view_cashin_requests(status_filter=status)
            print("Rows returned:", rows)  

            # rows are already dicts
            requests = rows
        except Exception as e:
            ctk.CTkLabel(self.cashin_list_frame, text=f"Error loading requests: {e}", text_color="red").pack(pady=20)
            return

        if not requests:
            ctk.CTkLabel(self.cashin_list_frame, text="No cash-in requests found.", text_color="gray").pack(pady=20)
            return

        for i, req in enumerate(requests):
            bg_color = "#F9F9F9" if i % 2 == 0 else "white"
            card = ctk.CTkFrame(self.cashin_list_frame, corner_radius=8, fg_color=bg_color)
            card.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(card, text=f"Request ID: {req['request_id']}", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card, text=f"Amount: ₱{float(req['amount']):.2f}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Status: {req['status']}").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Date: {req['date_requested']}", text_color="gray").pack(anchor="w", padx=10, pady=2)

            if req['status'].lower() == "pending":
                ctk.CTkButton(card, text="Cancel", width=100, height=30,
                            fg_color="#E57373", hover_color="#C62828",
                            command=lambda rid=req['request_id']: self.cancel_request(rid)).pack(anchor="e", padx=10, pady=5)

    def show_post_bills_frame(self):
        self.clear_content_frame()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Posted Bills",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=15)

        # Search Bar 
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(pady=5)

        self.bill_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search Bill ID",
            width=250
        )
        self.bill_search_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=self.refresh_posted_bills
        ).pack(side="left", padx=5)

        # Scrollable Bills List
        self.posted_bills_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=750
        )
        self.posted_bills_frame.pack(pady=10, fill="both", expand=True) # Use expand=True
 
        # Footer (Back button)
        footer = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        footer.pack(pady=10)

        ctk.CTkButton(
            footer,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("student") 
        ).pack()

        self.refresh_posted_bills()

    def load_organization_posts_handler(self, results_frame):
        # Clear old items
        for widget in results_frame.winfo_children():
            widget.destroy()

        try:
            rows = self.backend.load_organization_posts()

            if not rows:
                ctk.CTkLabel(results_frame, text="No organization posts found.", text_color="gray").pack(pady=20)
                return

            # Build cards for each post
            for i, row in enumerate(rows):
                bill_id, title, description, amount, org_name = row

                bg_color = "#F9F9F9" if i % 2 == 0 else "white"
                card = ctk.CTkFrame(results_frame, corner_radius=8, fg_color=bg_color)
                card.pack(fill="x", padx=10, pady=8)

                ctk.CTkLabel(card, text=f"{title}", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=2)
                ctk.CTkLabel(card, text=f"Organization: {org_name}", font=("Arial", 12)).pack(anchor="w", padx=10)
                ctk.CTkLabel(card, text=f"Amount: ₱{float(amount):.2f}", font=("Arial", 12)).pack(anchor="w", padx=10)
                ctk.CTkLabel(card, text=f"Description: {description}", font=("Arial", 11), wraplength=650).pack(anchor="w", padx=10, pady=2)
                ctk.CTkLabel(card, text=f"Bill ID: {bill_id}", text_color="gray", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)

        except Exception as e:
            ctk.CTkLabel(results_frame, text=f"Error loading posts: {e}", text_color="red").pack(pady=20)

    def refresh_posted_bills(self):
        # Clear old cards
        for widget in self.posted_bills_frame.winfo_children():
            widget.destroy()

        search_value = self.bill_search_entry.get().strip()
        bills = self.student_backend.view_posted_bills(search_value if search_value else None)

        if not bills:
            ctk.CTkLabel(
                self.posted_bills_frame,
                text="No posted bills found.",
                text_color="gray"
            ).pack(pady=20)
            return

        # Build cards for each bill
        for i, bill in enumerate(bills):
            bg_color = "#F9F9F9" if i % 2 == 0 else "white"
            card = ctk.CTkFrame(self.posted_bills_frame, corner_radius=10, fg_color=bg_color)
            card.pack(fill="x", padx=10, pady=8)

            # Bill Info
            ctk.CTkLabel(
                card,
                text=f"{bill['title']}",
                font=("Arial", 14, "bold")
            ).pack(anchor="w", padx=10, pady=2)

            ctk.CTkLabel(
                card,
                text=f"Organization: {bill.get('organization_name', 'N/A')}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Amount: ₱{float(bill['amount']):.2f}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Description: {bill['description']}",
                font=("Arial", 11),
                wraplength=650
            ).pack(anchor="w", padx=10, pady=2)

            ctk.CTkLabel(
                card,
                text=f"Bill ID: {bill['bill_id']}",
                text_color="gray",
                font=("Arial", 10)
            ).pack(anchor="w", padx=10, pady=2)

            # Pay Button
            ctk.CTkButton(
                card,
                text="Pay",
                width=120,
                fg_color="#4CAF50",
                hover_color="#43A047",
                command=lambda b_id=bill['bill_id']: self.pay_bill_handler(b_id)
            ).pack(anchor="e", padx=10, pady=8)

    def pay_bill_handler(self, bill_id, message_entry=None):
    # Optional message from textbox
        message = None
        if message_entry:
            message = message_entry.get("0.0", "end").strip()

        ok, result = self.student_backend.pay_organization_bill(bill_id, message)

        if ok:
            CTkMessagebox(
                title="Success",
                message=(
                    f"Bill paid successfully!\n"
                    f"Transaction ID: {result['transaction_id']}\n"
                    f"Organization: {result['organization']}\n"
                    f"Amount: ₱{result['amount']:.2f}"
                ),
                icon="info"
            )
            self._update_balance_display() # Update balance
            self.refresh_posted_bills() # Refresh the list of bills
        else:
            CTkMessagebox(
                title="Error",
                message=result,  # error string
                icon="cancel"
            )

    def stu_show_transaction_history(self):
        self.clear_content_frame()  # remove previous content

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Transaction History",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=15)

        # ===== Back Button at the top =====
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="⬅ Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("student")
        )
        back_btn.pack(pady=10, anchor="w")  # top-left

        # Scrollable frame for transactions 
        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Fetch transactions
        transactions = self.student_backend.view_transactions()

        if not transactions:
            ctk.CTkLabel(
                scroll_frame,
                text="No transactions found.",
                text_color="gray"
            ).pack(pady=20)
        else:
            for tx in transactions:
                card = ctk.CTkFrame(
                    scroll_frame,
                    fg_color="white",
                    corner_radius=15,
                    border_color="#e0e0e0",
                    border_width=2
                )
                card.pack(fill="x", pady=8, padx=5)
                card.pack_propagate(False)

                ctk.CTkLabel(
                    card,
                    text=(f"Date: {tx.get('created_at', 'N/A')}\n"
                          f"Direction: {tx.get('direction', 'N/A')}\n"
                          f"Sender: {tx.get('sender_name', 'N/A')}\n"
                          f"Receiver: {tx.get('receiver_name', 'N/A')}\n"
                          f"Amount: ₱{float(tx.get('amount', 0)):.2f}\n"
                          f"Type: {tx.get('transaction_type', 'N/A')}"),
                    font=("Times New Roman", 14),
                    justify="left"
                ).pack(padx=15, pady=15, anchor="w")

    def stu_pay_bill_handler(self, bill_id, message_entry=None):
        # Optional message from textbox
        message = None
        if message_entry:
            message = message_entry.get("0.0", "end").strip()

        ok, result = self.student_backend.pay_organization_bill(bill_id, message)

        if ok:
            CTkMessagebox(
                title="Success",
                message=(
                    f"Bill paid successfully!\n"
                    f"Transaction ID: {result['transaction_id']}\n"
                    f"Organization: {result['organization']}\n"
                    f"Amount: ₱{result['amount']:.2f}"
                ),
                icon="info"
            )
            self._update_balance_display() 
            self.stu_refresh_posted_bills() 
        else:
            CTkMessagebox(title="Error", message=result, icon="cancel")

    def org_post_bill_frame(self):
        # Clear previous content
        self.clear_content_frame()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Post Organization Bill",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=20)

        # Bill Title Entry
        self.bill_title_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Enter Bill Title",
            width=400,
            corner_radius=10,
            height=45
        )
        self.bill_title_entry.pack(pady=10)

        # Bill Description Entry
        self.bill_description_entry = ctk.CTkTextbox(
            self.content_frame,
            width=400,
            height=80,
            corner_radius=10
        )
        self.bill_description_entry.pack(pady=10)
        self.bill_description_entry.insert("0.0", "Enter description...")

        # Bill Amount Entry
        self.bill_amount_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Enter Amount",
            width=400,
            corner_radius=10,
            height=45
        )
        self.bill_amount_entry.pack(pady=10)

        # Post Bill Button
        print("About to create Post Bill button")
        post_bill_btn = ctk.CTkButton(
            self.content_frame,
            text="Post Bill",
            width=350,
            height=50,
            fg_color="#4CAF50",
            hover_color="#43A047",
            corner_radius=10,
            command=lambda: self.post_bill_handler(
                self.bill_title_entry.get(),
                self.bill_description_entry.get("0.0", "end").strip(),
                self.bill_amount_entry.get()
            )
        )
        post_bill_btn.pack(pady=20)
        print("Post Bill button created and packed")
        # Back Button
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("organization")
        )
        back_btn.pack(pady=10)


    def post_bill_handler(self, title_entry, description_entry, amount_entry):
        # Check if backend exists (updated from self.frontend)
        if self.organization_backend is None:
            CTkMessagebox(
                title="Error",
                message="Backend connection error. Please restart the application.",
                icon="cancel"
            )
            return
        
        # Call post_bill on the backend (updated from self.frontend)
        ok, result = self.organization_backend.post_bill(title_entry, description_entry, amount_entry)

        if ok:
            CTkMessagebox(
                title="Success",
                message=result,
                icon="check",
                option_1="OK"
            )
            self.show_content("organization")
        else:
            CTkMessagebox(
                title="Error",
                message=result,
                icon="cancel", 
                option_1="OK"
            )

  
    def org_request_cash_out_frame(self):
        # Clear previous content
        self.clear_content_frame()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Request Cash Out",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=20)

        # Amount Entry
        self.cash_out_amount_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Enter Amount",
            width=400,
            corner_radius=10,
            height=45
        )
        self.cash_out_amount_entry.pack(pady=10)

        # Optional Message Textbox
        self.cash_out_message_textbox = ctk.CTkTextbox(
            self.content_frame,
            width=400,
            height=120,
            corner_radius=10
        )
        self.cash_out_message_textbox.pack(pady=10)
        self.cash_out_message_textbox.insert("0.0", "Optional message...")

        # Submit Button
        submit_btn = ctk.CTkButton(
            self.content_frame,
            text="Submit Request",
            width=350,
            height=50,
            fg_color="#2196F3",
            hover_color="#1E88E5",
            corner_radius=10,
            command=lambda: self.request_cash_out_handler(
                self.cash_out_amount_entry.get(),
                self.cash_out_message_textbox.get("0.0", "end").strip()
            )
        )
        submit_btn.pack(pady=20)

        # Back Button
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("organization")  # return to org wallet main services
        )
        back_btn.pack(pady=10)

    def request_cash_out_handler(self, amount_entry, message_entry=None):

        ok, result = self.organization_backend.request_cash_out(amount_entry, message_entry)

        if ok:
            CTkMessagebox(
                title="Success",
                message=result,   
                icon="info"
            )
            self.show_main_services()
        else:
            CTkMessagebox(
                title="Error",
                message=result,   
                icon="cancel"
            )


    def org_view_cash_out_requests_frame(self):
        # Clear previous content
        self.clear_content_frame()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="View Cash-Out Requests",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=20)

        # Search and Filter Frame
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        filter_frame.pack(pady=10)

        # Request ID search
        self.cash_out_search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search Request ID",
            width=250
        )
        self.cash_out_search_entry.pack(side="left", padx=5)

        # Status filter dropdown
        self.cash_out_status = ctk.StringVar(value="All")
        status_options = ["All", "Pending", "Approved", "Rejected"]
        ctk.CTkOptionMenu(
            filter_frame,
            variable=self.cash_out_status,
            values=status_options
        ).pack(side="left", padx=5)

        # Search Button
        ctk.CTkButton(
            filter_frame,
            text="Search",
            width=100,
            command=self.refresh_cash_out_list
        ).pack(side="left", padx=5)

        # Scrollable Frame for Requests
        self.cash_out_list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=750
        )
        self.cash_out_list_frame.pack(pady=15, fill="both", expand=True) # Use expand=True
 
        # Back Button
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("organization")
        )
        back_btn.pack(pady=10)

        # Initial load
        self.refresh_cash_out_list()


    def refresh_cash_out_list(self):
        # Clear old items
        for widget in self.cash_out_list_frame.winfo_children():
            widget.destroy()

        search_value = self.cash_out_search_entry.get().strip()
        status_value = self.cash_out_status.get()
        if status_value == "All":
            status_value = None

        requests = self.organization_backend.view_cash_out_requests(request_id_search=search_value, status_filter=status_value)

        if not requests:
            ctk.CTkLabel(
                self.cash_out_list_frame,
                text="No cash-out requests found for the selected criteria.",
                text_color="gray"
            ).pack(pady=20)
            return

        for req in requests:
            card = ctk.CTkFrame(self.cash_out_list_frame, corner_radius=10)
            card.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(
                card,
                text=f"Request ID: {req['request_id']}",
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=10, pady=2)

            ctk.CTkLabel(
                card,
                text=f"Amount: ₱{req['amount']:.2f}"
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Status: {req['status'].capitalize()}"
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Requested: {req['date_requested']}",
                text_color="gray"
            ).pack(anchor="w", padx=10, pady=2)

            if req['date_processed']:
                ctk.CTkLabel(
                    card,
                    text=f"Processed: {req['date_processed']}",
                    text_color="gray"
                ).pack(anchor="w", padx=10, pady=2)


    def org_view_transactions_frame(self):
        # Clear previous content
        self.clear_content_frame()

        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="Organization Transactions",
            font=("Times New Roman", 25, "bold")
        ).pack(pady=20)

        # Search / Filter Frame
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        filter_frame.pack(pady=10)

        # Bill Title search
        self.transaction_search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search Bill Title",
            width=250
        )
        self.transaction_search_entry.pack(side="left", padx=5)

        # Search Button
        ctk.CTkButton(
            filter_frame,
            text="Search",
            width=100,
            command=self.refresh_transactions_list
        ).pack(side="left", padx=5)

        # Scrollable Frame for transactions
        self.transactions_list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=750
        )
        self.transactions_list_frame.pack(pady=15, fill="both", expand=True) # Use expand=True
 
        # Back Button
        back_btn = ctk.CTkButton(
            self.content_frame,
            text="Back",
            width=150,
            height=45,
            fg_color="#A8D9A4",
            corner_radius=10,
            command=lambda: self.show_content("organization")
        )
        back_btn.pack(pady=10)

        # Initial load
        self.refresh_transactions_list()

    def org_transaction_handler(self, sender_id_entry=None, date_entry=None):
        # Grab values from UI entries if provided
        sender_id_search = sender_id_entry.get().strip() if sender_id_entry else None
        date_filter = date_entry.get().strip() if date_entry else None

        # Call backend
        results = self.organization_backend.org_transaction(
            sender_id_search=sender_id_search,
            date_filter=date_filter
        )

        if results and len(results) > 0:
            CTkMessagebox(
                title="Transactions Found",
                message=f"{len(results)} transaction(s) retrieved successfully.",
                icon="info"
            )
            # Example: refresh or show them in a table/list view
            self.show_transactions(results)
        else:
            CTkMessagebox(
                title="No Transactions",
                message="No matching transactions were found.",
                icon="warning"
            )

    def refresh_transactions_list(self):
        # Clear old items
        for widget in self.transactions_list_frame.winfo_children():
            widget.destroy()

        search_value = self.transaction_search_entry.get().strip()

        transactions = self.organization_backend.view_transactions(bill_title=search_value if search_value else None)

        if not transactions:
            ctk.CTkLabel(
                self.transactions_list_frame,
                text="No transactions found.",
                text_color="gray"
            ).pack(pady=20)
            return

        for tx in transactions:
            card = ctk.CTkFrame(self.transactions_list_frame, corner_radius=10)
            card.pack(fill="x", padx=10, pady=8)

            ctk.CTkLabel(
                card,
                text=f"Transaction ID: {tx['transaction_id']}",
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=10, pady=2)

            ctk.CTkLabel(
                card,
                text=f"Bill: {tx['bill_title']} (ID: {tx['bill_id']})"
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Amount: ₱{tx['amount']:.2f}"
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Type: {tx['transaction_type'].capitalize()} | Status: {tx['status'].capitalize()}"
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Sender: {tx['student_name']} (ID: {tx['student_id']})"
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"Date: {tx['created_at']}",
                text_color="gray"
            ).pack(anchor="w", padx=10, pady=2)



if __name__ == "__main__":
    class MockWallet:
        def post_bill(self, title, desc, amount):
            print(f"Mock post_bill called with: {title}, {desc}, {amount}")
            return True, "Bill posted successfully (mock)."
        def get_balance(self):
            return 1234.56

    mock_student_wallet = MockWallet()
    mock_org_wallet = MockWallet()
    mock_user_data = {'id': 1, 'name': 'Test User'}

    app = StudentOrganizationDashboard(mock_student_wallet, mock_user_data, mock_org_wallet)
    app.mainloop()