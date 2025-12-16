"""
Finance Admin Wallet Module

This module handles all finance administrator operations for the Campus E-Wallet system.
It includes functionality for:

- Creating student wallet accounts with temporary passwords
- Viewing, approving, and rejecting cash-in requests
- Viewing, approving, and rejecting cash-out requests
- Retrieving transaction records for reporting and monitoring

The module interacts with the database layer for data persistence
and uses email services to send temporary login credentials.
"""

import bcrypt
import secrets
from system_backend.campusEwallet_db import execute_query, fetch_one, fetch_all
from system_backend.temp_pass_email_sender import send_temp_password

class FinanceAdminWallet:
    @staticmethod
    def admin_create_student_account(student_id, preview_only=False):
        """
        Create a student wallet account with a temporary password.
        
        Parameters:
            student_id (str): The ID of the student.
            preview_only (bool): If True, returns student info without creating the account.
        
        Returns:
            tuple: (bool, message/info dictionary)
        """
        try:
            # Fetch student details from enrolled students table
            student = fetch_one(
                "SELECT student_id, name, program, section, email, student_role, organization, treasurer_id "
                "FROM enrolled_students WHERE student_id = %s",
                (student_id,)
            )
            # If student does not exist, stop process
            if not student:
                return False, "Student ID not found in enrolled student records."

            # Preview mode returns student details without creating an account
            if preview_only:
                return True, {
                    "student_id": student["student_id"],
                    "name": student["name"],
                    "program": student["program"],
                    "section": student["section"],
                    "email": student["email"],
                    "role": student["student_role"],
                    "organization": student["organization"]
                }

            # Check if wallet user account already exists for this student
            exists = fetch_one(
                "SELECT user_id FROM wallet_users WHERE student_id = %s",
                (student_id,)
            )
            if exists:
                return False, "Account for this student already exists."

            # Generate temporary password and hash it
            temp_password = secrets.token_urlsafe(8)
            hashed_pw = bcrypt.hashpw(temp_password.encode(), bcrypt.gensalt())

            # Create wallet user account
            execute_query(
                "INSERT INTO wallet_users "
                "(student_id, email, user_password, role, created_by_admin, password_needs_change) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    student_id,
                    student["email"],
                    hashed_pw,
                    student["student_role"],
                    True,
                    True
                )
            )

            # Retrieve newly created user ID
            new_user = fetch_one(
                "SELECT user_id FROM wallet_users WHERE student_id = %s",
                (student_id,)
            )
            user_id = new_user["user_id"]

            # Create wallet with zero balance
            execute_query(
                "INSERT INTO wallets (user_id, balance) VALUES (%s, %s)",
                (user_id, 0.00)
            )

            # If student is a treasurer, create organization wallet if not existing
            if student["student_role"].lower() == "treasurer" and student["organization"]:
                exists = fetch_one(
                    "SELECT org_wallet_id FROM organization_wallets WHERE organization_name = %s",
                    (student["organization"],)
                )
                if not exists:
                    execute_query(
                        "INSERT INTO organization_wallets "
                        "(treasurer_id, organization_name, role, org_wallet_balance) "
                        "VALUES (%s, %s, %s, %s)",
                        (
                            student["treasurer_id"],
                            student["organization"],
                            student["student_role"],
                            0.00
                        )
                    )

            # Send temporary password via email
            try:
                send_temp_password(
                    recipient_email=student["email"],
                    temp_password=temp_password,
                    student_name=student["name"]
                )
            except Exception as e:
                return False, f"Account created but failed to send email: {e}"

            return True, "Student wallet account successfully created."

        except Exception as e:
            return False, str(e)


    @staticmethod
    def get_all_cashin_requests(search=None, status_filter="pending"):
        """
        Retrieve all cash-in requests with optional search and status filter.
        
        Parameters:
            search (str): Search term for request ID, student ID, or student name.
            status_filter (str): Filter by request status ('pending', 'approved', 'rejected', 'all').

        Returns:
            tuple: (bool, list of requests or error message)
        """
        try:
            params = []

            # Base query for cash-in requests
            query = """
                SELECT cr.request_id, cr.user_id, wu.student_id, es.name AS student_name,
                       cr.amount, cr.status, cr.date_requested
                FROM cashin_requests cr
                JOIN wallet_users wu ON cr.user_id = wu.user_id
                LEFT JOIN enrolled_students es ON wu.student_id = es.student_id
                WHERE 1=1
            """

            # Filter by request status
            if status_filter != "all":
                query += " AND cr.status = %s"
                params.append(status_filter)
            
            # Apply search filter
            if search:
                query += " AND (cr.request_id LIKE %s OR wu.student_id LIKE %s OR es.name LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param]*3)
            
            # Sort newest first
            query += " ORDER BY cr.date_requested DESC"

            results = fetch_all(query, tuple(params) if params else None)
            return True, results if results else []

        except Exception as e:
            return False, str(e)


    @staticmethod
    def get_all_cashout_requests(search=None, status_filter="pending"):
        """
        Retrieve all cash-out requests with optional search and status filter.

        Returns:
            tuple: (bool, list of requests or error message)
        """
        try:
            params = []

            # Base query for cash-out requests
            query = """
                SELECT cor.request_id, cor.org_wallet_id, cor.wallet_id,
                       ow.organization_name, ow.treasurer_id, es.name AS treasurer_name,
                       w.wallet_id AS service_wallet_id, wu.user_id AS service_user_id, wu.office_name AS service_name,
                       cor.amount, cor.message, cor.status, cor.date_requested, cor.date_processed
                FROM cashout_requests cor
                LEFT JOIN organization_wallets ow ON cor.org_wallet_id = ow.org_wallet_id
                LEFT JOIN enrolled_students es ON ow.treasurer_id = es.student_id
                LEFT JOIN wallets w ON cor.wallet_id = w.wallet_id
                LEFT JOIN wallet_users wu ON w.user_id = wu.user_id
                WHERE 1=1
            """

            # Filter by status
            if status_filter != "all":
                query += " AND cor.status = %s"
                params.append(status_filter)
            
            # Apply search filter
            if search:
                query += " AND (cor.request_id LIKE %s OR ow.organization_name LIKE %s OR wu.office_name LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param]*3)
            query += " ORDER BY cor.date_requested DESC"

            results = fetch_all(query, tuple(params) if params else None)

            # Replace missing names with N/A for display purposes
            for r in results:
                if r.get("org_wallet_id") and not r.get("treasurer_name"):
                    r["treasurer_name"] = "N/A"
                if r.get("wallet_id") and not r.get("service_name"):
                    r["service_name"] = "N/A"
            return True, results
        except Exception as e:
            return False, str(e)


    @staticmethod
    def approve_cashin_request(request_id, admin_user_id):
        """
        Approve a pending cash-in request and update wallet balance.

        Returns:
            tuple: (bool, message)
        """
        try:
            # Retrieve pending cash-in request
            request = fetch_one("""
                SELECT user_id, amount
                FROM cashin_requests
                WHERE request_id = %s AND status = 'pending'
            """, (request_id,))

            if not request:
                return False, "Cash-In request not found or already processed."

            user_id = request["user_id"]
            amount = request["amount"]

            # Add amount to user's wallet balance
            execute_query("""
                UPDATE wallets
                SET balance = balance + %s
                WHERE user_id = %s
            """, (amount, user_id))

            # Mark request as approved
            execute_query("""
                UPDATE cashin_requests
                SET status = 'approved'
                WHERE request_id = %s
            """, (request_id,))

            return True, "Cash-In request approved and wallet balance updated."

        except Exception as e:
            return False, str(e)

    @staticmethod
    def decline_cashin_request(request_id, reason=None):
        """Reject a cash-in request and optionally record a reason."""
        try:
            # Reject cash-in request and record reason
            execute_query(
                "UPDATE cashin_requests SET status='rejected', decline_reason=%s, date_processed=NOW() WHERE request_id=%s",
                (reason, request_id)
            )
            return True, "Cash-In request rejected."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def approve_cashout_request(request_id, admin_user_id):
        """
        Approve a pending cash-out request and deduct from wallets.

        Returns:
            tuple: (bool, message)
        """
        try:
            # Retrieve pending cash-out request
            req = fetch_one("""
                SELECT org_wallet_id, wallet_id, amount
                FROM cashout_requests
                WHERE request_id = %s AND status = 'pending'
            """, (request_id,))

            if not req:
                return False, "Cash-Out request not found or already processed."

            amount = req["amount"]

            # Deduct from organization wallet
            if req["org_wallet_id"]:
                execute_query("""
                    UPDATE organization_wallets
                    SET org_wallet_balance = org_wallet_balance - %s
                    WHERE org_wallet_id = %s
                """, (amount, req["org_wallet_id"]))

            # Deduct from service wallet
            elif req["wallet_id"]:
                execute_query("""
                    UPDATE wallets
                    SET balance = balance - %s
                    WHERE wallet_id = %s
                """, (amount, req["wallet_id"]))

            else:
                return False, "Invalid cash-out request."

            # Mark request as approved
            execute_query("""
                UPDATE cashout_requests
                SET status = 'approved'
                WHERE request_id = %s
            """, (request_id,))

            return True, "Cash-Out request approved."

        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def decline_cashout_request(request_id, reason=None):
        """Reject a cash-out request and optionally record a reason."""
        try:
            # Reject cash-out request and record reason
            execute_query(
                "UPDATE cashout_requests SET status='rejected', decline_reason=%s, date_processed=NOW() WHERE request_id=%s",
                (reason, request_id)
            )
            return True, "Cash-Out request rejected."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_all_transactions(filter_type=None, search=None, start_date=None, end_date=None):
        """
        Retrieve all transactions with optional filters.

        Parameters:
            filter_type (str): Optional transaction type filter.
            search (str): Optional transaction ID search.
            start_date (str): Optional start date filter (YYYY-MM-DD).
            end_date (str): Optional end date filter (YYYY-MM-DD).

        Returns:
            tuple: (bool, list of transactions or error message)
        """
        try:
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []
            
            # Filter by transaction type
            if filter_type:
                query += " AND transaction_type=%s"
                params.append(filter_type)
            
            # Search by transaction ID
            if search:
                query += " AND transaction_id LIKE %s"
                params.append(f"%{search}%")
            results = fetch_all(query, tuple(params) if params else None)
            return True, results if results else []
        except Exception as e:
            return False, str(e)