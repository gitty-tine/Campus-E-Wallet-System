import unittest
from unittest.mock import patch
import sys
import os
#This is the error occurs in unittest, change the changes directly into my files.
# ---------- FIX PATH ----------
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))  # two levels up
sys.path.insert(0, PROJECT_ROOT)

import system_backend.campusEwallet_db as campusEwallet_db
from system_backend.students_wallet import StudentWallet


class TestStudentWallet(unittest.TestCase):

    # -------------------------
    # STUDENT NAME
    # -------------------------
    @patch("system_backend.campusEwallet_db.fetch_one")
    def test_fetch_student_name_success(self, mock_fetch):
        mock_fetch.side_effect = [
            {"student_id": "20210001"},
            {"name": "Juan Dela Cruz"}
        ]
        wallet = StudentWallet(1)
        self.assertEqual(wallet.student_name, "Juan Dela Cruz")

    @patch("system_backend.campusEwallet_db.fetch_one")
    def test_fetch_student_name_not_found(self, mock_fetch):
        mock_fetch.return_value = None
        wallet = StudentWallet(1)
        self.assertIsNone(wallet.student_name)

    # -------------------------
    # BALANCE
    # -------------------------
    @patch("system_backend.campusEwallet_db.fetch_one")
    def test_display_balance_success(self, mock_fetch):
        # Provide return values for all calls to fetch_one in order:
        # 1. In __init__ for wallet_users to get student_id
        # 2. In __init__ for enrolled_students to get name
        # 3. In display_balance to get wallet balance
        mock_fetch.side_effect = [
            {"student_id": "20210001"},  # For _fetch_student_name
            {"name": "Juan Dela Cruz"},    # For _fetch_student_name
            {"balance": 500.75}         # For display_balance
        ]
        wallet = StudentWallet(1)
        self.assertEqual(wallet.display_balance(), 500.75)

    @patch("system_backend.campusEwallet_db.fetch_one")
    def test_display_balance_no_wallet(self, mock_fetch):
        # Mock the calls in __init__ and then the call in display_balance
        mock_fetch.side_effect = [
            {"student_id": "20210001"},
            {"name": "Juan Dela Cruz"},
            None  # This is for the display_balance call
        ]
        wallet = StudentWallet(1)
        self.assertEqual(wallet.display_balance(), 0.0)

    # -------------------------
    # SEND MONEY
    # -------------------------
    @patch("system_backend.campusEwallet_db.execute_query")
    @patch("system_backend.campusEwallet_db.fetch_one")
    def test_send_money_success(self, mock_fetch, mock_execute):
        # Mocks for __init__, sender balance, receiver info, receiver wallet existence
        mock_fetch.side_effect = [
            {"student_id": "SENDER-ID"}, # __init__
            {"name": "Sender Name"},     # __init__
            {"balance": 1000},  # sender wallet
            {"user_id": 2, "student_id": "20210002", "office_id": None,
             "office_name": None, "receiver_name": "Maria Cruz"},  # receiver
            {"user_id": 2}  # receiver wallet exists
        ]
        mock_execute.return_value = True

        wallet = StudentWallet(1)
        ok, result = wallet.send_money("20210002", 200, "Allowance")
        self.assertTrue(ok)
        self.assertEqual(result["amount"], 200)
        self.assertEqual(result["receiver_user_id"], 2)

    @patch("system_backend.campusEwallet_db.fetch_one")
    def test_send_money_insufficient_balance(self, mock_fetch):
        # Mocks for __init__ and then sender wallet balance
        mock_fetch.side_effect = [
            {"student_id": "SENDER-ID"},
            {"name": "Sender Name"},
            {"balance": 50},  # sender wallet
            {"user_id": 2, "student_id": "20210002", "office_id": None, "office_name": None, "receiver_name": "Maria Cruz"}, # receiver lookup
            {"user_id": 2} # receiver wallet exists
        ]
        wallet = StudentWallet(1)
        ok, msg = wallet.send_money("20210002", 200)
        self.assertFalse(ok)
        self.assertEqual(msg, "Insufficient balance.")

    def test_send_money_invalid_amount(self):
        # We need to patch the __init__ calls even for a simple test
        with patch("system_backend.campusEwallet_db.fetch_one") as mock_fetch:
            mock_fetch.side_effect = [
                {"student_id": "SENDER-ID"},
                {"name": "Sender Name"},
            ]
            wallet = StudentWallet(1)
        ok, msg = wallet.send_money("20210002", "abc")
        self.assertFalse(ok)
        self.assertEqual(msg, "Invalid amount format.")

    # -------------------------
    # REQUEST FUNDS
    # -------------------------
    @patch("system_backend.campusEwallet_db.execute_query")
    def test_request_funds_success(self, mock_execute):
        mock_execute.return_value = True
        # Patch the __init__ calls
        with patch("campusEwallet_db.fetch_one") as mock_fetch:
            mock_fetch.side_effect = [
                {"student_id": "SENDER-ID"},
                {"name": "Sender Name"},
            ]
            wallet = StudentWallet(1)
        ok, result = wallet.request_funds(300)
        self.assertTrue(ok)
        self.assertEqual(result["amount"], 300)
        self.assertEqual(result["status"], "pending")

    # -------------------------
    # VIEW CASH-IN REQUESTS
    # -------------------------
    @patch("system_backend.campusEwallet_db.fetch_all")
    def test_view_cashin_requests(self, mock_fetch_all):
        mock_fetch_all.return_value = [{"request_id": "REQ-1"}]
        # Patch the __init__ calls
        with patch("campusEwallet_db.fetch_one") as mock_fetch:
            mock_fetch.side_effect = [
                {"student_id": "SENDER-ID"},
                {"name": "Sender Name"},
            ]
            wallet = StudentWallet(1)
        results = wallet.view_cashin_requests()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)

    # -------------------------
    # ORGANIZATION POSTS
    # -------------------------
    @patch("system_backend.campusEwallet_db.fetch_all")
    def test_load_organization_posts(self, mock_fetch_all):
        mock_fetch_all.return_value = [{"bill_id": 1, "title": "Org Fee"}]
        # Patch the __init__ calls
        with patch("campusEwallet_db.fetch_one") as mock_fetch:
            mock_fetch.side_effect = [
                {"student_id": "SENDER-ID"},
                {"name": "Sender Name"},
            ]
            wallet = StudentWallet(1)
        results = wallet.load_organization_posts()
        self.assertEqual(results[0]["title"], "Org Fee")

    # -------------------------
    # PAY ORGANIZATION BILL
    # -------------------------
    @patch("system_backend.campusEwallet_db.execute_query")
    @patch("system_backend.campusEwallet_db.fetch_one")
    def test_pay_organization_bill_success(self, mock_fetch, mock_execute):
        mock_fetch.side_effect = [
            # For __init__
            {"student_id": "SENDER-ID"},
            {"name": "Sender Name"},
            # For pay_organization_bill
            {"amount": 200, "org_wallet_id": 1, "organization_name": "Org A"},
            # For get_balance inside pay_organization_bill
            {"balance": 500.0}
        ]
        mock_execute.return_value = True
        wallet = StudentWallet(user_id=1)
        ok, result = wallet.pay_organization_bill(1, "Payment for fees")
        self.assertTrue(ok)
        self.assertEqual(result["amount"], 200)
        self.assertEqual(result["organization"], "Org A")

    # -------------------------
    # VIEW TRANSACTIONS - This test was failing
    # -------------------------
    @patch("system_backend.campusEwallet_db.fetch_all")
    def test_view_transactions(self, mock_fetch_all):
        mock_fetch_all.return_value = [{"transaction_id": "TRNX-1"}]
        with patch("campusEwallet_db.fetch_one") as mock_fetch:
            mock_fetch.side_effect = [
                {"student_id": "SENDER-ID"},
                {"name": "Sender Name"},
            ]
            wallet = StudentWallet(1)
            # The call to view_transactions must be inside the patch block
            # so that mock_fetch_all is still active.
            results = wallet.view_transactions()
            self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()