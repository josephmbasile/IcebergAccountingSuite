import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from repository.invoice import InvoiceRepository


class TestInvoiceRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.invoice_repo = InvoiceRepository(self.mock_connection)

    @patch("repository.invoice.db")
    def test_create_table(self, mock_db):
        # Execute
        self.invoice_repo.create_table()

        # Assert
        mock_db.create_tables.assert_called_once()
        args, _ = mock_db.create_tables.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("CREATE TABLE IF NOT EXISTS tbl_Invoices", args[1])

    @patch("repository.invoice.db")
    def test_get_by_id(self, mock_db):
        # Setup
        invoice_id = 1
        expected_invoice = {"Invoice_ID": invoice_id, "Total": 100}
        mock_db.execute_read_query_dict.return_value = [expected_invoice]

        # Execute
        result = self.invoice_repo.get_by_id(invoice_id)

        # Assert
        self.assertEqual(result, expected_invoice)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"WHERE Invoice_ID = {invoice_id}", args[1])

    @patch("repository.invoice.db")
    def test_get_by_customer_id(self, mock_db):
        # Setup
        customer_id = 1
        expected_invoices = [{"Invoice_ID": 1, "Customer_ID": customer_id}]
        mock_db.execute_read_query_dict.return_value = expected_invoices

        # Execute
        result = self.invoice_repo.get_by_customer_id(customer_id)

        # Assert
        self.assertEqual(result, expected_invoices)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"WHERE Customer_ID = {customer_id}", args[1])

    @patch("repository.invoice.db")
    def test_search(self, mock_db):
        # Setup
        search_term = "INV-001"
        mock_db.execute_read_query_dict.return_value = [{"Invoice_ID": 1, "Tracking_Code": "INV-001"}]

        # Execute
        self.invoice_repo.search(search_term)

        # Assert
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"Tracking_Code LIKE '%{search_term}%'", args[1])

    @patch("repository.invoice.db")
    def test_insert(self, mock_db):
        # Execute
        self.invoice_repo.insert(
            customer_id=1,
            tracking_code="TRK123",
            line_items="[]",
            due_date="2023-01-01",
            created_time="Now",
            edited_time="Now",
            subtotal=100,
            sales_tax=10,
            total=110,
            status="Paid",
            payment_method="Credit",
            location="Store",
            invoice_id=99
        )

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("INSERT INTO tbl_Invoices", args[1])
        self.assertIn("99", args[1])  # Invoice ID
        self.assertIn("TRK123", args[1])

    @patch("repository.invoice.db")
    def test_update(self, mock_db):
        # Execute
        self.invoice_repo.update(
            invoice_id=1,
            status="Void",
            edited_time="Now"
        )

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("UPDATE tbl_Invoices SET", args[1])
        self.assertIn("Status = 'Void'", args[1])
        self.assertIn("WHERE Invoice_ID = 1", args[1])


    @patch("repository.invoice.db")
    def test_get_count(self, mock_db):
        mock_db.execute_read_query_dict.return_value = [{'COUNT(*)': 5}]
        count = self.invoice_repo.get_count()
        self.assertEqual(count, 5)
        mock_db.execute_read_query_dict.assert_called_with(
            self.mock_connection,
            "SELECT COUNT(*) FROM tbl_Invoices;"
        )

    @patch("repository.invoice.db")
    def test_get_totals_by_customer_and_status(self, mock_db):
        mock_db.execute_read_query_dict.return_value = [{'Total': 100}, {'Total': 200}]
        results = self.invoice_repo.get_totals_by_customer_and_status(1, ['Due', 'Overdue'])
        self.assertEqual(len(results), 2)
        expected_query = "SELECT Total FROM tbl_Invoices WHERE Customer_ID = 1 AND (Status = 'Due' OR Status = 'Overdue');"
        mock_db.execute_read_query_dict.assert_called_with(self.mock_connection, expected_query)

if __name__ == "__main__":
    unittest.main()
