import unittest
from unittest.mock import patch, MagicMock
import os, sys

# ---- FIX PATH ----
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from system_backend.students_wallet import StudentWallet


class TestStudentWallet(unittest.TestCase):

    @patch("system_backend.students_wallet.system_backend.campusEwallet_db.execute_query")
    @patch("system_backend.students_wallet.system_backend.campusEwallet_db.fetch_one")
    def test_pay_organization_bill_success(self, mock_fetch, mock_execute):
        """
        Tests the success path for paying an organization bill.
        """
        # Correctly mock all calls to fetch_one in order of execution:
        # 1. In StudentWallet.__init__ -> _fetch_student_name -> fetch_one (for user info)
        # 2. In pay_organization_bill -> get_balance -> fetch_one (for sender balance)
        # 3. In pay_organization_bill -> fetch_one (for bill details)
        mock_fetch.side_effect = [
            {"student_id": "2024-123"},  # Mock for _fetch_student_name (wallet_users)
            {"name": "John Doe"},        # Mock for _fetch_student_name (enrolled_students)
            {"amount": 200, "org_wallet_id": 1, "organization_name": "Org A"}, # Mock for bill details
            {"balance": 500.0},            # Mock for get_balance()
        ]
        mock_execute.return_value = True

        # This call will consume the first mock value
        wallet = StudentWallet(user_id=1)

        # This call will consume the next two mock values
        ok, result = wallet.pay_organization_bill(bill_id=1, message="Payment for fees")

        # Assertions
        self.assertTrue(ok, "The payment process should return True for success.")
        self.assertIn("transaction_id", result)
        self.assertEqual(result["amount"], 200)
        self.assertEqual(mock_execute.call_count, 3, "Should execute 3 queries: update sender, update org, insert transaction.")


if __name__ == "__main__":
    unittest.main()