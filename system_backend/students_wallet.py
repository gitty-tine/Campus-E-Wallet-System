"""
Student Wallet Backend Module

This module contains all backend logic related to a student's e-wallet account
in the Campus E-Wallet System.

Main Responsibilities:
- Generate unique transaction and request IDs
- Fetch student information linked to a wallet user
- Display wallet balance and welcome information
- Send money between users (students or offices)
- Request funds (cash-in requests)
- View and filter cash-in requests
- Load and pay organization bills
- View unpaid posted bills
- View complete transaction history

Dependencies:
- datetime, random: for ID generation and timestamps
- PIL (Image, ImageDraw, ImageFont): reserved for future receipt/image features
- system_backend.campusEwallet_db: database access layer

All database operations are handled through the campusEwallet_db module.
"""

from datetime import datetime
import random
from PIL import Image, ImageDraw, ImageFont
import os
import system_backend.campusEwallet_db


def generate_transaction_id():
    """
    Generate a unique transaction ID.

    Format: TRNX-YYYYMMDD-RANDOM

    Returns:
        str: Unique transaction ID.
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = random.randint(10000, 99999)
    return f"TRNX-{date_part}-{random_part}"


def generate_request_id():
    """
    Generate a unique cash-in request ID.

    Format: REQ-YYYYMMDD-RANDOM

    Returns:
        str: Unique request ID.
    """
    return f"REQ-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"


class StudentWallet:
    """
    Backend class for handling student wallet operations.

    Attributes:
        user_id (int): Wallet user ID.
        student_id (str): Linked student ID (if available).
        student_name (str): Name of the student (fetched from database).
    """
    def __init__(self, user_id):
        """
        Initialize a StudentWallet instance.

        Parameters:
            user_id (int): Wallet user ID.
        """
        self.user_id = user_id
        self.student_id = None
        self.student_name = self._fetch_student_name()

        if not self.student_name:
             print(f"Warning: Name not found for User ID {user_id}")


    def _fetch_student_name(self):
        """
        Fetch the student's name from the database based on user_id.

        Returns:
            str or None: Student name if found, else None.
        """
        try:
            user_info = system_backend.campusEwallet_db.fetch_one("SELECT student_id FROM wallet_users WHERE user_id = %s", (self.user_id,))
            self.student_id = user_info["student_id"] if user_info else None
            student_id = self.student_id

            if student_id:
                student_row = system_backend.campusEwallet_db.fetch_one("SELECT name FROM enrolled_students WHERE student_id = %s", (student_id,))
                return student_row["name"] if student_row else None

            return None

        except Exception as e:
            print(f"Database Error fetching student name: {e}")
            return None


    def display_welcome_info(self):
        """
        Generate a welcome message for the student.

        Returns:
            str: Welcome message including first name or generic user label.
        """
        current_balance = self.display_balance()
        
        if self.student_name:
            first_name = self.student_name.split()[0]
        else:
            first_name = f"User {self.user_id}"

        welcome_message = f"Welcome, {first_name}!"
        return welcome_message

    def display_balance(self):
        """
        Fetch the current balance of the user's wallet.

        Returns:
            float: Wallet balance, 0.0 if not found or on error.
        """
        try:
            row = system_backend.campusEwallet_db.fetch_one("SELECT balance FROM wallets WHERE user_id = %s", (self.user_id,))
            print("DEBUG: row from wallets:", row)
            return float(row["balance"]) if row and row["balance"] is not None else 0.0
        except Exception as e:
            print(f"Database Error in display_balance: {e}")
            return 0.0

    def get_balance(self):
        """
        Get the wallet balance (wrapper for display_balance).

        Returns:
            float: Wallet balance.
        """
        return self.display_balance()


    def send_money(self, receiver_identifier, amount, message=None):
        """
        Send money from the user's wallet to another student or office.

        Parameters:
            receiver_identifier (str): Receiver's student or office ID.
            amount (float or str): Amount to transfer.
            message (str, optional): Optional message for the transaction.

        Returns:
            tuple: (bool, dict/str)
                True and transaction details if successful,
                False and error message otherwise.
        """
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid amount format."

        if amount <= 0:
            return False, "Amount must be greater than zero."

        try:
            sender_wallet = system_backend.campusEwallet_db.fetch_one("SELECT balance FROM wallets WHERE user_id = %s", (self.user_id,))
            if not sender_wallet:
                return False, "Sender wallet not found in the system."
            if sender_wallet["balance"] < amount:
                return False, "Insufficient balance."

            receiver = system_backend.campusEwallet_db.fetch_one("""
                SELECT wu.user_id, wu.student_id, wu.office_id, wu.office_name, es.name AS receiver_name
                FROM wallet_users wu
                LEFT JOIN enrolled_students es ON wu.student_id = es.student_id
                WHERE wu.student_id = %s OR wu.office_id = %s
            """, (receiver_identifier, receiver_identifier))

            if not receiver or not receiver.get("user_id"):
                return False, "Receiver not found with the provided identifier."
                
            receiver_user_id = receiver["user_id"]
            if receiver_user_id == self.user_id:
                return False, "Cannot send money to yourself."
            
            receiver_wallet = system_backend.campusEwallet_db.fetch_one("SELECT user_id FROM wallets WHERE user_id = %s", (receiver_user_id,))
            if not receiver_wallet:
                 return False, "Receiver wallet does not exist."

            system_backend.campusEwallet_db.execute_query("UPDATE wallets SET balance = balance - %s WHERE user_id = %s", (amount, self.user_id))
            system_backend.campusEwallet_db.execute_query("UPDATE wallets SET balance = balance + %s WHERE user_id = %s", (amount, receiver_user_id))

            trx_id = generate_transaction_id()

            system_backend.campusEwallet_db.execute_query("""
                INSERT INTO transactions
                (transaction_id, sender_id, receiver_id, amount, transaction_type, service_paid_for, created_at, status, message)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)
            """, (trx_id, self.user_id, receiver_user_id, amount, "Send Money", None, "completed", message))
            
            result = {
                "transaction_id": trx_id,
                "sender_user_id": self.user_id,
                "receiver_user_id": receiver_user_id,
                "amount": amount,
                "status": "completed",
                "message": message
            }
            if receiver.get("student_id"):
                result["receiver_student_id"] = receiver["student_id"]
                result["receiver_name"] = receiver.get("receiver_name")
            if receiver.get("office_id"):
                result["receiver_office_id"] = receiver["office_id"]
                result["receiver_office_name"] = receiver.get("office_name")

            result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True, result

        except Exception as e:
            print(f"FATAL ERROR in send_money: {e}")
            return False, f"A system error occurred during the transfer: {str(e)}"


    def request_funds(self, amount):
        """
        Submit a cash-in request for the user's wallet.

        Parameters:
            amount (float or str): Amount requested.

        Returns:
            tuple: (bool, dict/str)
                True and request details if successful,
                False and error message otherwise.
        """
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid amount format."

        if amount <= 0:
            return False, "Amount must be greater than zero."

        try:
            request_id = generate_request_id()

            ok = system_backend.campusEwallet_db.execute_query("""
                INSERT INTO cashin_requests
                (request_id, user_id, amount, status, date_requested)
                VALUES (%s, %s, %s, 'pending', NOW())
            """, (request_id, self.user_id, amount))

            if not ok:
                return False, "Database error while submitting cash-in request."

            result = {
                "request_id": request_id,
                "user_id": self.user_id,
                "amount": amount,
                "status": "pending"
            }

            return True, result

        except Exception as e:
            print(f"Database Error in request_funds: {e}")
            return False, f"A system error occurred during the request: {str(e)}"
    

    def view_cashin_requests(self, search_id=None, status_filter=None):
        """
        Retrieve cash-in requests for the user, optionally filtered by ID or status.

        Parameters:
            search_id (str, optional): Partial request ID to filter.
            status_filter (str, optional): Status filter ('pending', 'completed', etc.)

        Returns:
            list: List of cash-in requests.
        """
        query = """
            SELECT request_id, amount, status, date_requested
            FROM cashin_requests
            WHERE user_id = %s
        """
        params = [self.user_id]

        if search_id:
            query += " AND request_id LIKE %s"
            params.append(f"%{search_id}%")

        if status_filter:
            # normalize to lowercase
            query += " AND LOWER(status) = %s"
            params.append(status_filter.lower())

        query += " ORDER BY date_requested DESC"
        return system_backend.campusEwallet_db.fetch_all(query, tuple(params))


    def load_organization_posts(self):
        query = """
            SELECT ob.bill_id, ob.title, ob.description, ob.amount,
                   ow.organization_name
            FROM organization_bills ob
            JOIN organization_wallets ow ON ob.org_wallet_id = ow.org_wallet_id
            ORDER BY ob.bill_id DESC
        """
        return system_backend.campusEwallet_db.fetch_all(query)

    def pay_organization_bill(self, bill_id, message=None):
        bill = system_backend.campusEwallet_db.fetch_one("""
            SELECT ob.amount, ob.org_wallet_id, ow.organization_name
            FROM organization_bills ob
            JOIN organization_wallets ow ON ob.org_wallet_id = ow.org_wallet_id
            WHERE ob.bill_id = %s
        """, (bill_id,))

        if not bill:
            return False, "Bill not found."

        amount = float(bill["amount"])

        if self.get_balance() < amount:
            return False, "Insufficient balance."

        trx_id = generate_transaction_id()

        system_backend.campusEwallet_db.execute_query(
            "UPDATE wallets SET balance = balance - %s WHERE user_id = %s",
            (amount, self.user_id)
        )

        system_backend.campusEwallet_db.execute_query(
            "UPDATE organization_wallets SET org_wallet_balance = org_wallet_balance + %s WHERE org_wallet_id = %s",
            (amount, bill["org_wallet_id"])
        )

       
        system_backend.campusEwallet_db.execute_query("""
            INSERT INTO transactions
                (transaction_id, sender_id, amount,
                 transaction_type, bill_id, status, message)
            VALUES (%s, %s, %s, 'Bill Payment', %s, 'completed', %s)
        """, (trx_id, self.user_id, amount, bill_id, message))

        return True, {
            "transaction_id": trx_id,
            "amount": amount,
            "organization": bill["organization_name"]
        }
    

    def view_posted_bills(self, bill_id_search=None):
        """
        Returns a list of posted bills from 'organization_bills' that the current user has not yet paid.
        """
        query = """
            SELECT ob.bill_id, ob.org_wallet_id, ob.title, ob.description, ob.amount,
                   ow.organization_name
            FROM organization_bills ob
            JOIN organization_wallets ow ON ob.org_wallet_id = ow.org_wallet_id
            WHERE NOT EXISTS (
                SELECT 1
                FROM transactions t
                WHERE t.bill_id = ob.bill_id
                  AND t.sender_id = %s
                  AND t.transaction_type = 'Bill Payment'
                  AND t.status = 'completed'
            )
        """
        params = [self.user_id]

        if bill_id_search:
            query += " AND ob.bill_id LIKE %s"
            params.append(f"%{bill_id_search}%")

        query += " ORDER BY ob.bill_id DESC"
        return system_backend.campusEwallet_db.fetch_all(query, tuple(params))

    def get_posted_bills_summary(self, bill_id_search=None):
        return self.view_posted_bills(bill_id_search)

    def view_transactions(self):
        """
        View all transactions for the user (sent and received).
        """
        query = """
            SELECT
                t.transaction_id,
                t.amount,
                t.transaction_type,
                t.created_at,
                t.status,
                t.message,
                -- Determine if it's an incoming or outgoing transaction
                CASE
                    WHEN t.sender_id = %s THEN 'Outgoing'
                    ELSE 'Incoming'
                END AS direction,
                -- Get Sender Name
                COALESCE(sender_student.name, sender_office.office_name, 'System') AS sender_name,
                -- Get Receiver Name
                CASE
                    WHEN t.transaction_type = 'Bill Payment' THEN org.organization_name
                    ELSE COALESCE(receiver_student.name, receiver_office.office_name, 'System')
                END AS receiver_name
            FROM transactions t
            -- Join for Sender Info
            LEFT JOIN wallet_users sender_wu ON t.sender_id = sender_wu.user_id
            LEFT JOIN enrolled_students sender_student ON sender_wu.student_id = sender_student.student_id
            LEFT JOIN wallet_users sender_office ON t.sender_id = sender_office.user_id AND sender_office.office_id IS NOT NULL
            -- Join for Receiver Info
            LEFT JOIN wallet_users receiver_wu ON t.receiver_id = receiver_wu.user_id
            LEFT JOIN enrolled_students receiver_student ON receiver_wu.student_id = receiver_student.student_id
            LEFT JOIN wallet_users receiver_office ON t.receiver_id = receiver_office.user_id AND receiver_office.office_id IS NOT NULL
            -- Join for Bill Payment Info
            LEFT JOIN organization_bills ob ON t.bill_id = ob.bill_id
            LEFT JOIN organization_wallets org ON ob.org_wallet_id = org.org_wallet_id
            WHERE t.sender_id = %s OR t.receiver_id = %s
            ORDER BY t.created_at DESC;
        """
        return system_backend.campusEwallet_db.fetch_all(query, (self.user_id, self.user_id, self.user_id))

    