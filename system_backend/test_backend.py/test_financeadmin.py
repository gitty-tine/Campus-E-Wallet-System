# test_backend/test_financeadmin.py

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root and system_backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # system_backend folder

# Mock campusEwallet_db and temp_pass_email_sender so imports in finance_admin_wallet work
sys.modules['campusEwallet_db'] = MagicMock()
sys.modules['temp_pass_email_sender'] = MagicMock()

from system_backend import finance_admin_wallet  # Correct import of your FinanceAdminWallet class


class TestFinanceAdminWallet(unittest.TestCase):

    @patch('system_backend.finance_admin_wallet.fetch_one')
    @patch('system_backend.finance_admin_wallet.execute_query')
    @patch('system_backend.finance_admin_wallet.send_temp_password')
    def test_admin_create_student_account_preview(self, mock_send_email, mock_execute, mock_fetch):
        # Mock student record
        mock_fetch.return_value = {
            "student_id": "S12345",
            "name": "Test Student",
            "program": "BSCS",
            "section": "1A",
            "email": "student@test.com",
            "student_role": "Student",
            "organization": None,
            "treasurer_id": None
        }

        # Preview only
        success, data = finance_admin_wallet.FinanceAdminWallet.admin_create_student_account("S12345", preview_only=True)
        self.assertTrue(success)
        self.assertEqual(data["student_id"], "S12345")
        mock_execute.assert_not_called()
        mock_send_email.assert_not_called()

    @patch('system_backend.finance_admin_wallet.fetch_one')
    @patch('system_backend.finance_admin_wallet.execute_query')
    @patch('system_backend.finance_admin_wallet.send_temp_password')
    def test_admin_create_student_account_success(self, mock_send_email, mock_execute, mock_fetch):
        # Mock student record + existing wallet check + new user_id
        student_record = {
            "student_id": "S12345",
            "name": "Test Student",
            "program": "BSCS",
            "section": "1A",
            "email": "student@test.com",
            "student_role": "Student",
            "organization": None,
            "treasurer_id": None
        }
        mock_fetch.side_effect = [student_record, None, {"user_id": 1}]

        success, msg = finance_admin_wallet.FinanceAdminWallet.admin_create_student_account("S12345")
        self.assertTrue(success)
        self.assertEqual(msg, "Student wallet account successfully created.")
        self.assertTrue(mock_execute.called)
        self.assertTrue(mock_send_email.called)

    @patch('system_backend.finance_admin_wallet.fetch_all')
    def test_get_all_cashin_requests(self, mock_fetch_all):
        mock_fetch_all.return_value = [
            {"request_id": "CR001", "user_id": 1, "student_id": "S12345", "student_name": "Test",
             "amount": 100, "status": "pending", "date_requested": "2025-01-01"}
        ]
        success, results = finance_admin_wallet.FinanceAdminWallet.get_all_cashin_requests()
        self.assertTrue(success)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["request_id"], "CR001")

    @patch('system_backend.finance_admin_wallet.fetch_all')
    def test_get_all_cashout_requests(self, mock_fetch_all):
        mock_fetch_all.return_value = [
            {
                "request_id": "CO001",
                "org_wallet_id": 1,
                "wallet_id": None,
                "organization_name": "Org1",
                "treasurer_id": "S123",
                "treasurer_name": "N/A",   
                "service_wallet_id": None,
                "service_user_id": None,
                "service_name": None,       
                "amount": 50,
                "message": "Test",
                "status": "pending",
                "date_requested": "2025-01-01",
                "date_processed": None
            }
        ]
        success, results = finance_admin_wallet.FinanceAdminWallet.get_all_cashout_requests()
        self.assertTrue(success)
        self.assertEqual(results[0]["treasurer_name"], "N/A")
        self.assertIsNone(results[0]["service_name"])  # expect None


    @patch('system_backend.finance_admin_wallet.fetch_one')
    @patch('system_backend.finance_admin_wallet.execute_query')
    def test_approve_cashin_request(self, mock_execute, mock_fetch):
        mock_fetch.return_value = {"user_id": 1, "amount": 100}
        success, msg = finance_admin_wallet.FinanceAdminWallet.approve_cashin_request("CR001", 1)
        self.assertTrue(success)
        self.assertIn("approved", msg)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('system_backend.finance_admin_wallet.execute_query')
    def test_decline_cashin_request(self, mock_execute):
        success, msg = finance_admin_wallet.FinanceAdminWallet.decline_cashin_request("CR001", "Invalid")
        self.assertTrue(success)
        self.assertIn("rejected", msg)
        mock_execute.assert_called_once()

    @patch('system_backend.finance_admin_wallet.fetch_one')
    @patch('system_backend.finance_admin_wallet.execute_query')
    def test_approve_cashout_request_org_wallet(self, mock_execute, mock_fetch):
        mock_fetch.return_value = {"org_wallet_id": 1, "wallet_id": None, "amount": 100}
        success, msg = finance_admin_wallet.FinanceAdminWallet.approve_cashout_request("CO001", 1)
        self.assertTrue(success)
        self.assertIn("approved", msg)
        self.assertEqual(mock_execute.call_count, 2)

    @patch('system_backend.finance_admin_wallet.fetch_one')
    @patch('system_backend.finance_admin_wallet.execute_query')
    def test_approve_cashout_request_invalid(self, mock_execute, mock_fetch):
        mock_fetch.return_value = {"org_wallet_id": None, "wallet_id": None, "amount": 100}
        success, msg = finance_admin_wallet.FinanceAdminWallet.approve_cashout_request("CO002", 1)
        self.assertFalse(success)
        self.assertIn("Invalid", msg)

    @patch('system_backend.finance_admin_wallet.execute_query')
    def test_decline_cashout_request(self, mock_execute):
        success, msg = finance_admin_wallet.FinanceAdminWallet.decline_cashout_request("CO001", "Invalid")
        self.assertTrue(success)
        self.assertIn("rejected", msg)
        mock_execute.assert_called_once()

    @patch('system_backend.finance_admin_wallet.fetch_all')
    def test_get_all_transactions(self, mock_fetch_all):
        mock_fetch_all.return_value = [
            {"transaction_id": "TRX001", "transaction_type": "cash-in", "amount": 100}
        ]
        success, results = finance_admin_wallet.FinanceAdminWallet.get_all_transactions()
        self.assertTrue(success)
        self.assertEqual(results[0]["transaction_id"], "TRX001")


if __name__ == "__main__":
    unittest.main()