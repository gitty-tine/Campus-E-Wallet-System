import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import time
import bcrypt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  


import system_backend.registration as reg


class TestRegistrationBackend(unittest.TestCase):

    def setUp(self):
        # Clear verification codes and verified_students before each test
        reg.verification_codes.clear()
        reg.verified_students.clear()
        
    def test_validate_student_id(self):
        self.assertEqual(reg.validate_student_id("12345"), (True, None))
        self.assertEqual(reg.validate_student_id(""), (False, "Student ID must be a non-empty string."))
        self.assertEqual(reg.validate_student_id(None), (False, "Student ID must be a non-empty string."))

    def test_validate_password(self):
        self.assertEqual(reg.validate_password("password123"), (True, None))
        self.assertEqual(reg.validate_password("short"), (False, "Password must be at least 8 characters."))

    def test_generate_verification_code(self):
        code = reg.generate_verification_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    @patch('system_backend.registration.fetch_one')
    @patch('system_backend.registration.send_verification_email')
    def test_verify_student_success(self, mock_send_email, mock_fetch_one):
        mock_fetch_one.return_value = {"email": "student@test.com"}

        msg = reg.verify_student("12345")
        self.assertEqual(msg, "Verification code sent to your student email.")
        self.assertIn("12345", reg.verification_codes)
        mock_send_email.assert_called_once()

    @patch('system_backend.registration.fetch_one')
    def test_verify_student_not_found(self, mock_fetch_one):
        mock_fetch_one.return_value = None
        msg = reg.verify_student("12345")
        self.assertEqual(msg, "Student ID does not exist in records.")

    def test_verify_code_success(self):
        reg.verification_codes["12345"] = {
            "code": "654321",
            "expires_at": time.time() + 300
        }
        with patch('system_backend.registration.fetch_one') as mock_fetch:
            mock_fetch.return_value = {"name": "Test Student", "email": "student@test.com"}
            result, student_info = reg.verify_code("12345", "654321")
            self.assertTrue(result)
            self.assertEqual(student_info["student_id"], "12345")

    def test_verify_code_incorrect(self):
        reg.verification_codes["12345"] = {"code": "654321", "expires_at": time.time() + 300}
        result, msg = reg.verify_code("12345", "123456")
        self.assertFalse(result)
        self.assertEqual(msg, "Incorrect verification code.")

    def test_verify_code_expired(self):
        reg.verification_codes["12345"] = {"code": "654321", "expires_at": time.time() - 1}
        msg = reg.verify_code("12345", "654321")
        self.assertEqual(msg, "Verification code expired. Request a new one.")


    @patch('system_backend.registration.fetch_one')
    @patch('system_backend.registration.execute_query')
    def test_create_account_success(self, mock_execute, mock_fetch):
        reg.verified_students.add("12345")
        # Mock fetch_one for checking account existence
        mock_fetch.side_effect = [
            None,  # No existing account
            {"email": "student@test.com", "student_role": "Student", "organization": None, "treasurer_id": None},
            {"user_id": 1}  # Return user_id after insert
        ]

        result, msg = reg.create_account("12345", "password123", "password123")
        self.assertTrue(result)
        self.assertEqual(msg, "Account successfully created!")
        self.assertNotIn("12345", reg.verified_students)
        self.assertTrue(mock_execute.called)

    def test_create_account_not_verified(self):
        result, msg = reg.create_account("12345", "password123", "password123")
        self.assertFalse(result)
        self.assertEqual(msg, "Please verify your email first.")

    def test_create_account_password_mismatch(self):
        reg.verified_students.add("12345")
        result, msg = reg.create_account("12345", "password123", "password321")
        self.assertFalse(result)
        self.assertEqual(msg, "Passwords do not match.")


if __name__ == "__main__":
    unittest.main()