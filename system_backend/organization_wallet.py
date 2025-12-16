"""
OrganizationWallet Module

This module handles organization-level wallet operations for the campus
e-wallet system. It is primarily designed for **organization treasurers**
who are authorized to manage their organization’s shared funds.

Main Responsibilities:
- Load and validate an organization wallet linked to a treasurer
- Display and retrieve organization wallet balances
- Post organization bills for members to pay
- View organization-related transactions and bill payments
- Submit and track cash-out (withdrawal) requests
- Filter transactions and cash-out requests by status, date, or identifier

Authorization Rules:
- Only students with the role **treasurer** can access and manage
  an organization wallet
- Wallet access is validated using the student's enrolled organization
  and role

Data Sources:
- enrolled_students
- organization_wallets
- organization_bills
- transactions
- cashout_requests
- wallet_users

Dependencies:
- campusEwallet_db for database queries and updates
- datetime for timestamp and request ID generation
- CTkMessagebox for GUI error feedback during login

This module is intended to be used by backend services and GUI controllers
that require organization wallet functionality.
"""

from system_backend.campusEwallet_db import fetch_one, fetch_all, execute_query
from datetime import datetime
import random
from CTkMessagebox import CTkMessagebox


class OrganizationWallet:
    """
        Initialize the OrganizationWallet instance.

        Parameters:
            student_id (str): ID of the student (treasurer)
    """
    def __init__(self, student_id):
        self.student_id = str(student_id).strip()
        self.org_wallet_id = None


    def _load_org_wallet(self):
        """
        Load organization wallet info for the current student if they are a treasurer.
        Returns a dict with wallet and student info, or None if not found.

        Returns:
            dict or None: Dictionary containing student and wallet info if found,
            None if the wallet cannot be loaded or user is unauthorized.
        """
        query = """
            SELECT es.student_id, 
                es.name, 
                es.student_role AS role, 
                TRIM(es.organization) AS organization_name,
                ow.org_wallet_id, 
                ow.org_wallet_balance
            FROM enrolled_students es
            JOIN organization_wallets ow
            ON TRIM(es.organization) = TRIM(ow.organization_name)
            WHERE es.student_id = %s
            AND LOWER(TRIM(es.student_role)) = 'treasurer'
            LIMIT 1
        """
        row = fetch_one(query, (self.student_id,))

        # Debug output to check the fetched row
        if row:
            print("DEBUG row:", row)
            print("Student ID:", row.get("student_id"))
            print("Wallet ID:", row.get("org_wallet_id"))

        # If no wallet found, reset org_wallet_id
        if not row:
            self.org_wallet_id = None
            return None

        # Set wallet ID if found
        self.org_wallet_id = row["org_wallet_id"]
        return row


    def display_balance(self):
        """
        Return basic info about the organization wallet, including balance.
        Returns None if wallet cannot be loaded.

        Returns:
            dict or None: Dictionary containing student name, role, organization, and balance. None if wallet cannot be loaded.
        """
        info = self._load_org_wallet()
        if not info:
            return None

        return {
            "student_name": info.get("name", "Unknown"),
            "role": info.get("role", "Unknown"),
            "organization_name": info.get("organization_name", "Unknown"),
            "balance": float(info.get("org_wallet_balance", 0.0))
        }

    
    def get_balance(self):
        """
        Return the organization wallet balance for the current student.
        Returns None if wallet does not exist or cannot be loaded.

        Returns:
            float or None: Wallet balance. None if wallet cannot be loaded.
        """
        info = self.display_balance()
        if info and "balance" in info:
            return float(info["balance"])  # this is mapped from org_wallet_balance in display_balance
        return None


   
    def post_bill(self, title, description, amount):
        """
        Allows a treasurer to post a new bill for their organization.
        Validates title and amount before inserting into the database.

        Parameters:
            title (str): Title of the bill.
            description (str): Description or details of the bill.
            amount (float): Amount to be paid.

        Returns:
            tuple: (bool, str) Status of the operation and message.
        """
        if not self.org_wallet_id:
            # Ensure wallet is loaded
            if not self._load_org_wallet():
                return False, "You are not authorized to post bills. Only organization treasurers can post bills."

        # Validate title
        if not title or not title.strip():
            return False, "Title is required."

        # Validate amount
        try:
            amount = float(amount)
        except ValueError:
            return False, "Invalid amount."

        # Insert the bill into the organization_bills table
        query = """
            INSERT INTO organization_bills
                (org_wallet_id, title, description, amount)
            VALUES (%s, %s, %s, %s)
        """
        ok = execute_query(query, (self.org_wallet_id, title, description, amount))
        if ok:
            return True, f"Bill '{title}' posted successfully."
        return False, "Failed to post bill."

   
    def view_transactions(self, bill_title=None, sort_by="date"):
        """
        View all transactions associated with the organization's bills.
        Can filter by bill title and sort by date or title.

        Parameters:
            bill_title (str, optional): Filter transactions by bill title.
            sort_by (str, optional): 'date' or 'title' to sort transactions.

        Returns:
            list: List of transactions as dictionaries.
        """
        if not self.org_wallet_id:
            if not self._load_org_wallet():
                return []

        # Base query to fetch transactions
        query = """
            SELECT 
                t.transaction_id,
                t.amount,
                t.transaction_type,
                t.status,
                t.created_at,
                ob.bill_id,
                ob.title AS bill_title,
                wu.student_id,
                es.name AS student_name
            FROM transactions t
            JOIN organization_bills ob ON t.bill_id = ob.bill_id
            JOIN wallet_users wu ON t.sender_id = wu.user_id
            LEFT JOIN enrolled_students es ON wu.student_id = es.student_id
            WHERE ob.org_wallet_id = %s
        """
        params = [self.org_wallet_id]

        # Filter by bill title if provided
        if bill_title:
            query += " AND ob.title = %s"
            params.append(bill_title)

        # Sort either by title or date
        query += " ORDER BY ob.title ASC" if sort_by == "title" else " ORDER BY t.created_at DESC"

        return fetch_all(query, tuple(params))

    
    def request_cash_out(self, amount, message=None):
        """
        Submit a cash-out (withdrawal) request for the organization wallet.
        Generates a unique request ID and inserts it into cashout_requests.

        Parameters:
            amount (float): Amount to withdraw.
            message (str, optional): Optional note/message for the request.

        Returns:
            tuple: (bool, str) Status and feedback message.
        """
        if not self.org_wallet_id:
            if not self._load_org_wallet():
                return False, "Organization wallet not found."

        # Validate amount
        try:
            amount = float(amount)
        except:
            return False, "Invalid amount."

        if amount <= 0:
            return False, "Amount must be greater than zero."

        # Generate unique request ID
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000,99999)}"
        query = """
            INSERT INTO cashout_requests
                (request_id, org_wallet_id, amount, message, status, date_requested)
            VALUES (%s, %s, %s, %s, 'pending', NOW())
        """
        ok = execute_query(query, (request_id, self.org_wallet_id, amount, message))
        if ok:
            return True, f"Cash-out request submitted. ID: {request_id}"
        return False, "Failed to submit cash-out request."

    
    def view_cash_out_requests(self, request_id_search=None, status_filter=None):
        """
        View all cash-out requests for the organization wallet.
        Can filter by request ID or status ('pending', 'approved', 'rejected').

        Parameters:
            request_id_search (str, optional): Filter by request ID.
            status_filter (str, optional): Filter by request status: 'pending', 'approved', 'rejected'.

        Returns:
            list: List of cash-out request dictionaries.
        """
        if not self.org_wallet_id:
            if not self._load_org_wallet():
                return []

        query = """
            SELECT request_id, amount, message, status,
                   date_requested, date_processed
            FROM cashout_requests
            WHERE org_wallet_id = %s
        """
        params = [self.org_wallet_id]

        # Filter by request ID pattern
        if request_id_search:
            query += " AND request_id LIKE %s"
            params.append(f"%{request_id_search}%")

        # Filter by request status
        if status_filter and status_filter.lower() in ["pending", "approved", "rejected"]:
            query += " AND status = %s"
            params.append(status_filter.lower())

        query += " ORDER BY date_requested DESC"
        return fetch_all(query, tuple(params))

    def org_transaction(self, sender_id_search=None, date_filter=None):
        """
        View general transactions for the organization wallet.
        Can filter by sender ID or transaction date.

        Parameters:
            sender_id_search (str, optional): Filter by sender ID.
            date_filter (str, optional): Filter by transaction date (YYYY-MM-DD).

        Returns:
            list: List of transaction dictionaries.
        """
        if not self.org_wallet_id:
            if not self._load_org_wallet():
                return []

        query = """
            SELECT transaction_id, sender_id, receiver_id, service_id,
                amount, transaction_type, service_paid_for,
                created_at, status, message, bill_id
            FROM transactions
            WHERE org_wallet_id = %s
            AND (transaction_type IS NULL OR transaction_type = '')
        """
        params = [self.org_wallet_id]

        # Optional filters
        if sender_id_search:
            query += " AND sender_id = %s"
            params.append(sender_id_search)

        if date_filter:
            query += " AND DATE(created_at) = %s"
            params.append(date_filter)

        query += " ORDER BY created_at DESC"
        return fetch_all(query, tuple(params))


def login_user(email, password):
    """
    Authenticate a user by email and password.
    Returns a tuple: (user_data dict, OrganizationWallet instance)
    Shows a CTkMessagebox on login failure.

    Parameters:
        email (str): User email.
        password (str): User password.

    Returns:
        tuple: (user_data dict, OrganizationWallet instance) if successful,
               (None, None) if login fails.
    """
    query = """
        SELECT user_id, role, email, student_id
        FROM wallet_users
        WHERE email = %s AND password = %s
        LIMIT 1
    """
    user_data = fetch_one(query, (email, password))
    if not user_data:
        # GUI feedback for invalid login
        CTkMessagebox(title="Error", message="Invalid login", icon="cancel")
        return None, None

    # Instantiate an OrganizationWallet for the logged-in student
    wallet = OrganizationWallet(user_data["student_id"])
    return user_data, wallet
