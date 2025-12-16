import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import bcrypt
import os, sys

# ---- FIX PATH ----
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from login import LoginSystem


class TestLoginSystem(unittest.TestCase):

    def setUp(self):
        self.login = LoginSystem()

        self.student_user = {
            "user_id": 1,
            "student_id": "20210001",
            "office_id": None,
            "email": "student@test.com",
            "role": "student",
            "user_password": bcrypt.hashpw(b"password123", bcrypt.gensalt()),
            "failed_attempts": 0,
            "last_failed_time": None,
            "password_needs_change": 0
        }

        self.finance_admin = {
            "user_id": 2,
            "student_id": None,
            "office_id": "FIN001",
            "email": "admin@test.com",
            "role": "finance admin",
            "user_password": "adminpass",
            "failed_attempts": 0,
            "last_failed_time": None,
            "password_needs_change": 0
        }

    # -------------------------
    # LOGIN TESTS
    # -------------------------

    @patch("login.fetch_one")
    def test_login_success_student(self, mock_fetch):
        mock_fetch.return_value = self.student_user

        res = self.login.login("20210001", "password123")

        self.assertTrue(res["ok"])
        self.assertEqual(res["msg"], "Login successful.")

    @patch("login.fetch_one")
    def test_login_invalid_password(self, mock_fetch):
        user = dict(self.student_user)
        user["failed_attempts"] = 1

        mock_fetch.side_effect = [user, user]

        res = self.login.login("20210001", "wrongpass")

        self.assertFalse(res["ok"])
        self.assertIn("remaining_attempts", res["data"])

    @patch("login.fetch_one")
    def test_login_account_locked(self, mock_fetch):
        user = dict(self.student_user)
        user["failed_attempts"] = 5
        user["last_failed_time"] = datetime.now()

        mock_fetch.return_value = user

        res = self.login.login("20210001", "password123")

        self.assertFalse(res["ok"])
        self.assertIn("Account locked", res["msg"])

    @patch("login.fetch_one")
    def test_login_finance_admin_plain_password(self, mock_fetch):
        mock_fetch.return_value = self.finance_admin

        res = self.login.login("FIN001", "adminpass")

        self.assertTrue(res["ok"])

    # -------------------------
    # FORGOT PASSWORD
    # -------------------------

    @patch("login.send_password_reset_email")
    @patch("login.execute_query")
    @patch("login.fetch_one")
    def test_forgot_password_request_success(
        self, mock_fetch, mock_execute, mock_send_email
    ):
        mock_fetch.side_effect = [
            self.student_user,  # _find_user
            None                # no existing reset
        ]

        res = self.login.forgot_password_request("20210001")

        self.assertTrue(res["ok"])
        mock_send_email.assert_called_once()

    @patch("login.fetch_one")
    def test_forgot_password_user_not_found(self, mock_fetch):
        mock_fetch.return_value = None

        res = self.login.forgot_password_request("999")

        self.assertFalse(res["ok"])

    # -------------------------
    # VERIFY CODE
    # -------------------------

    @patch("login.execute_query")
    @patch("login.fetch_one")
    def test_verify_code_success(self, mock_fetch, mock_execute):
        mock_fetch.side_effect = [
            self.student_user,
            {
                "id": 1,
                "code": "123456",
                "expires_at": datetime.now() + timedelta(minutes=5)
            }
        ]

        res = self.login.verify_code("20210001", "123456")

        self.assertTrue(res["ok"])

    @patch("login.fetch_one")
    def test_verify_code_invalid(self, mock_fetch):
        mock_fetch.side_effect = [
            self.student_user,
            {
                "id": 1,
                "code": "999999",
                "expires_at": datetime.now() + timedelta(minutes=5)
            }
        ]

        res = self.login.verify_code("20210001", "123456")

        self.assertFalse(res["ok"])

    # -------------------------
    # RESET PASSWORD
    # -------------------------

    @patch("login.execute_query")
    @patch("login.fetch_one")
    def test_reset_password_success(self, mock_fetch, mock_execute):
        mock_fetch.side_effect = [
            self.student_user,
            {"id": 1, "verified_at": datetime.now()}
        ]

        res = self.login.reset_password(
            "20210001", "newpassword123", "newpassword123"
        )

        self.assertTrue(res["ok"])

    def test_reset_password_mismatch(self):
        res = self.login.reset_password(
            "20210001", "pass1", "pass2"
        )

        self.assertFalse(res["ok"])

    def test_reset_password_too_short(self):
        res = self.login.reset_password(
            "20210001", "short", "short"
        )

        self.assertFalse(res["ok"])

    @patch("login.execute_query")
    @patch("login.fetch_one")
    def test_force_change_password(self, mock_fetch, mock_execute):
        mock_fetch.return_value = self.student_user

        res = self.login.reset_password(
            "20210001",
            "newpassword123",
            "newpassword123",
            force_change=True
        )

        self.assertTrue(res["ok"])


if __name__ == "__main__":
    unittest.main()