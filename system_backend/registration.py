"""
Student Signup & Verification Module

This module handles **student account registration** for the campus e-wallet
system, including email verification, password validation, and wallet setup.

Main Features:
- Student ID validation against enrolled student records
- Email-based verification code generation and validation
- Resend cooldown and maximum resend attempt enforcement
- Secure password hashing using bcrypt
- Wallet account creation after successful email verification
- Automatic organization wallet creation for treasurers

Verification Flow:
1. Student requests verification → verification code sent to student email
2. Student enters verification code → code is validated and marked verified
3. Student creates account → wallet and (if applicable) organization wallet created

Security Controls:
- Verification codes expire after a fixed time window
- Limited resend attempts with cooldown
- Password length enforcement
- bcrypt password hashing
- Prevents duplicate account creation

Dependencies:
- campusEwallet_db for database operations
- signup_email_sender for sending verification emails
- mysql.connector for database error handling
- bcrypt for secure password hashing

This module is intended to be used by backend services or GUI controllers
responsible for student onboarding and account creation.
"""

from mysql.connector import Error
from system_backend.campusEwallet_db import fetch_one, execute_query
from system_backend.signup_email_sender import send_verification_email
import random
import time
import bcrypt

# Stores temporary verification codes for students
verification_codes = {}

# Tracks students who have successfully verified their email
verified_students = set()


def generate_verification_code(length=6):
    """
    Generate a numeric verification code.

    Parameters:
        length (int): Length of the verification code (default: 6)

    Returns:
        str: A string of digits representing the verification code
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def validate_student_id(student_id):
    """
    Validate the student ID format.

    Parameters:
        student_id (str): Student ID to validate

    Returns:
        tuple: (bool, str) True if valid, False and error message if invalid
    """
    if not isinstance(student_id, str) or not student_id.strip():
        return False, "Student ID must be a non-empty string."
    return True, None

def validate_password(password):
    """
    Validate password length.

    Parameters:
        password (str): Password to validate

    Returns:
        tuple: (bool, str) True if valid, False and error message if invalid
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters."
    return True, None


def validate_code_input(code):
    """
    Validate verification code format.

    Parameters:
        code (str): Verification code to validate

    Returns:
        tuple: (bool, str) True if valid, False and error message if invalid
    """
    if not isinstance(code, str) or not code.isdigit() or len(code) != 6:
        return False, "Invalid verification code."
    return True, None


def verify_student(student_id):
    """
    Send a verification code to the student's email.

    Parameters:
        student_id (str): Student ID to verify

    Returns:
        str: Success or error message
    """
    valid, msg = validate_student_id(student_id)
    if not valid:
        return msg

    try:
        # Check if student exists
        student = fetch_one("SELECT email FROM enrolled_students WHERE student_id = %s", (student_id,))
        if not student:
            return "Student ID does not exist in records."

        email = student["email"]
        current_time = time.time()

        # Handle resend logic
        if student_id in verification_codes:
            data = verification_codes[student_id]
            if data["resend_attempts"] >= 5:
                return "Maximum resend attempts reached."
            if current_time - data["last_sent"] < 30:
                wait_time = int(30 - (current_time - data["last_sent"]))
                return f"Please wait {wait_time} seconds before requesting another code."
            data["resend_attempts"] += 1
        else:
            verification_codes[student_id] = {"resend_attempts": 0}

        # Generate verification code
        code = generate_verification_code()
        verification_codes[student_id].update({
            "code": code,
            "expires_at": current_time + 300,  # 5 minutes expiry
            "last_sent": current_time
        })

        # Send email with the verification code
        try:
            send_verification_email(email, code)
        except Exception:
            return "Failed to send verification email. Check your internet connection."

        return "Verification code sent to your student email."

    except Error as e:
        return f"Database error: {str(e)}"


def verify_code(student_id, entered_code):
    """
    Verify the entered verification code.

    Parameters:
        student_id (str): Student ID
        entered_code (str): Verification code entered by the student

    Returns:
        tuple: (bool, dict or str) True and student info if successful,
               False and error message if invalid
    """
    valid, msg = validate_student_id(student_id)
    if not valid:
        return msg
    valid, msg = validate_code_input(entered_code)
    if not valid:
        return msg

    if student_id not in verification_codes:
        return "No verification code found. Request a new one."

    data = verification_codes[student_id]

    # Check expiry
    if time.time() > data["expires_at"]:
        del verification_codes[student_id]
        return "Verification code expired. Request a new one."

    # Check code match
    if entered_code != data["code"]:
        return False, "Incorrect verification code."

    # Success: mark student as verified
    verified_students.add(student_id)
    del verification_codes[student_id]

    student = fetch_one("SELECT name, email FROM enrolled_students WHERE student_id = %s", (student_id,))
    if not student:
        return False, "Student information not found."

    return True, {"student_id": student_id, "name": student["name"], "email": student["email"]}


def create_account(student_id, password, confirm_password):
    """
    Create a wallet account after successful email verification.

    Parameters:
        student_id (str): Student ID
        password (str): Chosen password
        confirm_password (str): Password confirmation

    Returns:
        tuple: (bool, str) True and success message if account created,
               False and error message if failed
    """
    if student_id not in verified_students:
        return False, "Please verify your email first."
    if password != confirm_password:
        return False, "Passwords do not match."

    valid, msg = validate_password(password)
    if not valid:
        return False, msg

    try:
        # Prevent duplicate account creation
        if fetch_one("SELECT user_id FROM wallet_users WHERE student_id = %s", (student_id,)):
            verified_students.discard(student_id)
            return False, "Account already exists."

        # Get student info and role
        student = fetch_one(
            "SELECT email, student_role, organization, treasurer_id FROM enrolled_students WHERE student_id = %s",
            (student_id,)
        )
        if not student:
            return False, "Student information not found."

        # Hash password securely
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Insert wallet user
        execute_query(
                """
                INSERT INTO wallet_users (
                    student_id,
                    email,
                    user_password,
                    role,
                    password_needs_change,
                    failed_attempts
                )
                VALUES (%s, %s, %s, %s, 0, 0)
                """,
                (student_id, student["email"], hashed_pw, student["student_role"])
            )

        # Get user_id
        user_id = fetch_one("SELECT user_id FROM wallet_users WHERE student_id = %s", (student_id,))["user_id"]

        # Create user wallet
        execute_query("INSERT INTO wallets (user_id, balance) VALUES (%s, %s)", (user_id, 0.00))

        # If treasurer, create organization wallet if not exists
        if student["student_role"].lower() == "treasurer" and student["organization"]:
            if not fetch_one("SELECT org_wallet_id FROM organization_wallets WHERE organization_name = %s",
                             (student["organization"],)):
                execute_query(
                    "INSERT INTO organization_wallets (treasurer_id, organization_name, role, org_wallet_balance) "
                    "VALUES (%s, %s, %s, %s)",
                    (student["treasurer_id"], student["organization"], student["student_role"], 0.00)
                )

        verified_students.discard(student_id)
        return True, "Account successfully created!"

    except Error as e:
        return False, f"Database error: {str(e)}"