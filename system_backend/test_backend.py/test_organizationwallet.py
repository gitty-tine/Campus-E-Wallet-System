import unittest
from unittest.mock import patch
import os, sys

# ---- FIX PATH ----
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from system_backend.organization_wallet import OrganizationWallet


class TestOrganizationWallet(unittest.TestCase):

    def setUp(self):
        self.wallet = OrganizationWallet("24-74745")

        self.org_wallet_row = {
            "org_wallet_id": 10,
            "org_wallet_balance": 1500.50
        }

    # -------------------------
    # LOAD & BALANCE
    # -------------------------

    @patch("system_backend.organization_wallet.fetch_one")
    def test_get_balance_success(self, mock_fetch):
        mock_fetch.return_value = self.org_wallet_row

        balance = self.wallet.get_balance()

        assert balance == 1500.50
        assert self.wallet.org_wallet_id == 10

    @patch("system_backend.organization_wallet.fetch_one")
    def test_get_balance_no_wallet(self, mock_fetch):
        mock_fetch.return_value = None

        balance = self.wallet.get_balance()

        assert balance is None

    # -------------------------
    # POST BILL
    # -------------------------

    @patch("system_backend.organization_wallet.execute_query")
    @patch("system_backend.organization_wallet.fetch_one")
    def test_post_bill_success(self, mock_fetch, mock_execute):
        mock_fetch.return_value = self.org_wallet_row
        mock_execute.return_value = True

        ok, msg = self.wallet.post_bill(
            "Electric Bill", "January utilities", 500
        )

        assert ok is True
        assert "posted successfully" in msg.lower()

    def test_post_bill_empty_title(self):
        ok, msg = self.wallet.post_bill("", "desc", 100)

        assert ok is False
        assert msg == "Title is required."

    @patch("system_backend.organization_wallet.fetch_one")
    def test_post_bill_invalid_amount(self, mock_fetch):
        mock_fetch.return_value = self.org_wallet_row

        ok, msg = self.wallet.post_bill(
            "Bill", "desc", "abc"
        )

        assert ok is False
        assert msg == "Invalid amount."

    # -------------------------
    # VIEW TRANSACTIONS
    # -------------------------

    @patch("system_backend.organization_wallet.fetch_all")
    @patch("system_backend.organization_wallet.fetch_one")
    def test_view_transactions_success(self, mock_fetch, mock_fetch_all):
        mock_fetch.return_value = self.org_wallet_row
        mock_fetch_all.return_value = [
            {"transaction_id": "TRX-1", "amount": 100}
        ]

        results = self.wallet.view_transactions()

        assert isinstance(results, list)
        assert len(results) == 1

    @patch("system_backend.organization_wallet.fetch_one")
    def test_view_transactions_no_wallet(self, mock_fetch):
        mock_fetch.return_value = None

        results = self.wallet.view_transactions()

        assert results == []

    # -------------------------
    # CASH OUT REQUEST
    # -------------------------

    @patch("system_backend.organization_wallet.execute_query")
    @patch("system_backend.organization_wallet.fetch_one")
    def test_request_cash_out_success(self, mock_fetch, mock_execute):
        mock_fetch.return_value = self.org_wallet_row
        mock_execute.return_value = True

        ok, msg = self.wallet.request_cash_out(300, "For event")

        assert ok is True
        assert "cash-out request submitted" in msg.lower()
        assert "REQ-" in msg

    @patch("system_backend.organization_wallet.fetch_one")
    def test_request_cash_out_invalid_amount(self, mock_fetch):
        mock_fetch.return_value = self.org_wallet_row

        ok, msg = self.wallet.request_cash_out("abc")

        assert ok is False
        assert msg == "Invalid amount."

    # -------------------------
    # VIEW CASH OUT REQUESTS
    # -------------------------

    @patch("system_backend.organization_wallet.fetch_all")
    @patch("system_backend.organization_wallet.fetch_one")
    def test_view_cash_out_requests_success(self, mock_fetch, mock_fetch_all):
        mock_fetch.return_value = self.org_wallet_row
        mock_fetch_all.return_value = [
            {"request_id": "REQ-1", "status": "pending"}
        ]

        results = self.wallet.view_cash_out_requests()

        assert isinstance(results, list)
        assert len(results) == 1

    @patch("system_backend.organization_wallet.fetch_one")
    def test_view_cash_out_requests_no_wallet(self, mock_fetch):
        mock_fetch.return_value = None

        results = self.wallet.view_cash_out_requests()

        assert results == []


if __name__ == "__main__":
    unittest.main()