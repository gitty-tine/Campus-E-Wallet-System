"""
LoginSystem Module

This module provides a secure authentication and password recovery system
for the campus e-wallet application.

Main Features:
- Secure login with bcrypt password hashing
- Failed login attempt tracking with temporary account lockout
- Support for legacy plain-text passwords (backward compatibility)
- Forgot-password flow using email-based verification codes
- Verification code expiration and resend cooldown handling
- Forced password change support for first-time or admin-created accounts
- Password reset with validation and security checks

Security Controls:
- Maximum login attempts before lockout
- Time-based lockout enforcement
- Verification codes with expiration time
- Minimum password length enforcement

Dependencies:
- bcrypt for password hashing and verification
- campusEwallet_db for database operations
- resetpass_email_sender for sending password reset emails

This class is intended to be used by backend services or APIs handling
user authentication and credential management.
"""

import bcrypt
from datetime import datetime, timedelta
import random
import string
from system_backend.campusEwallet_db import fetch_one, execute_query
from system_backend.resetpass_email_sender import send_password_reset_email


class LoginSystem:
    """
    LoginSystem handles authentication, password reset, and account security.

    Attributes:
        MAX_ATTEMPTS (int): Maximum failed login attempts before lockout.
        LOCKOUT_SECONDS (int): Duration of account lockout in seconds.
        VERIFICATION_CODE_LENGTH (int): Default length of verification codes.
        VERIFICATION_EXPIRE_MINUTES (int): Expiration time of codes in minutes.
        RESEND_COOLDOWN_SECONDS (int): Minimum wait time before resending codes.
        RESET_PASSWORD_WINDOW (int): Time window to complete a password reset.
        PASSWORD_MIN_LEN (int): Minimum allowed password length.
    """

    MAX_ATTEMPTS = 5
    LOCKOUT_SECONDS = 180
    VERIFICATION_CODE_LENGTH = 6
    VERIFICATION_EXPIRE_MINUTES = 10
    RESEND_COOLDOWN_SECONDS = 60
    RESET_PASSWORD_WINDOW = 5 * 60 
    PASSWORD_MIN_LEN = 8

    def __init__(self):
        """Initialize LoginSystem instance (no additional setup required)."""
        pass

    # Utility functions
    def _hash_password(self, password):
        """
        Hash a password using bcrypt.

        Parameters:
            password (str): Plain text password.

        Returns:
            bytes: Bcrypt hashed password.
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def _check_password(self, password, hashed):
        """
        Verify a password against a hash, supporting legacy plain-text passwords.

        Parameters:
            password (str): Plain text password.
            hashed (str or bytes): Stored hashed or plain-text password.

        Returns:
            bool: True if password matches, False otherwise.
        """
        if isinstance(hashed, str):
            hashed = hashed.encode()
        if not hashed.startswith(b'$2b$'):
            # Plain text password (for backward compatibility)
            return password.encode() == hashed
        try:
            return bcrypt.checkpw(password.encode(), hashed)
        except ValueError as e:
            print(f"Password check failed: {e}")
            return False

    def _generate_code(self, length=None):
        """
        Generate a numeric verification code.

        Parameters:
            length (int, optional): Length of the code. Defaults to VERIFICATION_CODE_LENGTH.

        Returns:
            str: Random numeric code.
        """
        length = length or self.VERIFICATION_CODE_LENGTH
        return ''.join(random.choice(string.digits) for _ in range(length))


    # User helper
    def _find_user(self, input_id):
        """
        Retrieve a user by student ID or office ID.

        Parameters:
            input_id (str): Student or office ID.

        Returns:
            dict or None: User record if found, else None.
        """
        query = """
        SELECT * FROM wallet_users
        WHERE student_id = %s OR office_id = %s
        LIMIT 1
        """
        return fetch_one(query, (input_id, input_id))

    def _reset_failed_attempts(self, user_id):
        """
        Reset failed login attempts for a user.

        Parameters:
            user_id (int): User identifier.
        """
        query = """
        UPDATE wallet_users
        SET failed_attempts = 0,
            last_failed_time = NULL
        WHERE user_id = %s
        """
        execute_query(query, (user_id,))

    def _increment_failed_attempts(self, user_id):
        """
        Increment failed login attempts and update last failed time.

        Parameters:
            user_id (int): User identifier.
        """
        query = """
        UPDATE wallet_users
        SET failed_attempts = failed_attempts + 1,
            last_failed_time = NOW()
        WHERE user_id = %s
        """
        execute_query(query, (user_id,))

    def _is_locked(self, user):
        """
        Check if a user's account is temporarily locked.

        Parameters:
            user (dict): User record.

        Returns:
            tuple: (is_locked (bool), remaining_seconds (int))
        """
        failed = user.get("failed_attempts") or 0
        last_failed = user.get("last_failed_time")
        if failed < self.MAX_ATTEMPTS:
            return False, 0
        if last_failed is None:
            self._reset_failed_attempts(user["user_id"])
            return False, 0

        if isinstance(last_failed, str):
            last_failed = datetime.fromisoformat(last_failed)

        elapsed = (datetime.now() - last_failed).total_seconds()
        if elapsed < self.LOCKOUT_SECONDS:
            return True, int(self.LOCKOUT_SECONDS - elapsed)
        else:
            self._reset_failed_attempts(user["user_id"])
            return False, 0

    # Login
    def login(self, input_id, password):
        """
        Attempt user login with ID and password.

        Parameters:
            input_id (str): Student or office ID.
            password (str): Plain text password.

        Returns:
            dict: Result with keys 'ok', 'msg', and optionally 'data'.
        """
        user = self._find_user(input_id)
        if not user:
            return {"ok": False, "msg": "Invalid ID or password."}

        locked, secs = self._is_locked(user)
        if locked:
            return {"ok": False, "msg": f"Account locked. Try again in {secs} seconds."}

        if self._check_password(password, user["user_password"]):
            self._reset_failed_attempts(user["user_id"])

            # Check if user has a temporary password (admin-assisted account), but skip for treasurer
            if user.get("password_needs_change") and user["role"] != "treasurer":
                return {
                    "ok": True,
                    "msg": "Login successful. You must change your temporary password.",
                    "data": {
                        "user_id": user["user_id"],
                        "role": user["role"],
                        "email": user["email"],
                        "student_id": user.get("student_id"), # Add student_id
                        "must_change_password": True
                    }
                }

            return {
                "ok": True,
                "msg": "Login successful.",
                "data": {
                    "user_id": user["user_id"],
                    "role": user["role"],
                    "email": user["email"],
                    "student_id": user.get("student_id"), # Add student_id
                    "must_change_password": False
                }
            }

        else:
            self._increment_failed_attempts(user["user_id"])
            refreshed = self._find_user(input_id)
            remaining = self.MAX_ATTEMPTS - refreshed.get("failed_attempts", 0)
            if remaining <= 0:
                return {
                    "ok": False,
                    "msg": f"Too many failed attempts. Account locked for {self.LOCKOUT_SECONDS} seconds."
                }
            else:
                return {
                    "ok": False,
                    "msg": "Invalid ID or password.",
                    "data": {"remaining_attempts": remaining}
                }


    # Forgot password
    def forgot_password_request(self, input_id):
        """
        Initiate forgot-password flow by sending a verification code via email.

        Parameters:
            input_id (str): Student or office ID.

        Returns:
            dict: Result with keys 'ok' and 'msg'.
        """
        user = self._find_user(input_id)
        if not user or not user.get("email"):
            return {"ok": False, "msg": "ID not found or no email registered."}

        code = self._generate_code()
        expires = datetime.now() + timedelta(minutes=self.VERIFICATION_EXPIRE_MINUTES)

        existing = fetch_one(
            "SELECT id, resend_count, last_sent FROM password_resets WHERE user_id = %s AND verified_at IS NULL",
            (user["user_id"],)
        )

        if existing:
            last_sent = existing.get("last_sent")
            resend_count = existing.get("resend_count") or 0
            cooldown = self.RESEND_COOLDOWN_SECONDS if resend_count >= 1 else 0
            if last_sent:
                if isinstance(last_sent, str):
                    last_sent = datetime.fromisoformat(last_sent)
                elapsed = (datetime.now() - last_sent).total_seconds()
                if elapsed < cooldown:
                    wait = int(cooldown - elapsed)
                    return {"ok": False, "msg": f"Please wait {wait} seconds before resending code."}

            # update code
            query = """
            UPDATE password_resets
            SET code = %s, resend_count = resend_count + 1, last_sent = NOW(), expires_at = %s, verified_at = NULL
            WHERE id = %s
            """
            execute_query(query, (code, expires, existing["id"]))
        else:
            # new reset request
            query = """
            INSERT INTO password_resets (user_id, code, resend_count, last_sent, expires_at)
            VALUES (%s, %s, 0, NOW(), %s)
            """
            execute_query(query, (user["user_id"], code, expires))

        # send email
        try:
            send_password_reset_email(user["email"], code)
        except Exception as e:
            return {"ok": False, "msg": f"Failed to send email: {e}"}

        return {"ok": True, "msg": "Verification code sent to your email."}

    def verify_code(self, input_id, code):
        """
        Verify a password reset code.

        Parameters:
            input_id (str): Student or office ID.
            code (str): Verification code received via email.

        Returns:
            dict: Result with keys 'ok' and 'msg'.
        """
        user = self._find_user(input_id)
        if not user:
            return {"ok": False, "msg": "ID not found."}

        reset = fetch_one(
            "SELECT * FROM password_resets WHERE user_id=%s AND verified_at IS NULL ORDER BY created_at DESC LIMIT 1",
            (user["user_id"],)
        )
        if not reset:
            return {"ok": False, "msg": "No active reset request."}

        expires_at = reset["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)

        if datetime.now() > expires_at:
            execute_query("DELETE FROM password_resets WHERE user_id=%s", (user["user_id"],))
            return {"ok": False, "msg": "Verification code expired. Request new code."}

        if str(reset["code"]) != str(code).strip():
            return {"ok": False, "msg": "Invalid code."}

        execute_query("UPDATE password_resets SET verified_at=NOW() WHERE id=%s", (reset["id"],))
        return {"ok": True, "msg": "Verification successful. You can now reset your password."}


    def reset_password(self, input_id, new_password, confirm_password, force_change=False):
        """
        Reset a user's password after verification or force change.

        Parameters:
            input_id (str): Student or office ID.
            new_password (str): New password.
            confirm_password (str): Confirmation of the new password.
            force_change (bool): Skip verification for first-time login. Defaults to False.

        Returns:
            dict: Result with keys 'ok' and 'msg'.
        """
        if new_password != confirm_password:
            return {"ok": False, "msg": "Passwords do not match."}
        if len(new_password) < self.PASSWORD_MIN_LEN:
            return {"ok": False, "msg": f"Password must be at least {self.PASSWORD_MIN_LEN} characters."}

        user = self._find_user(input_id)
        if not user:
            return {"ok": False, "msg": "ID not found."}

        # If this is a forced password change (first-time login), skip verified reset check
        if not force_change:
            reset = fetch_one(
                "SELECT * FROM password_resets WHERE user_id=%s AND verified_at IS NOT NULL ORDER BY verified_at DESC LIMIT 1",
                (user["user_id"],)
            )
            if not reset:
                return {"ok": False, "msg": "No verified reset request."}

        hashed = self._hash_password(new_password)
        execute_query(
            "UPDATE wallet_users SET user_password=%s, password_needs_change=0 WHERE user_id=%s",
            (hashed, user["user_id"])
        )
        if not force_change:
            execute_query("DELETE FROM password_resets WHERE user_id=%s", (user["user_id"],))
        self._reset_failed_attempts(user["user_id"])

        return {"ok": True, "msg": "Password updated. You can now log in."}