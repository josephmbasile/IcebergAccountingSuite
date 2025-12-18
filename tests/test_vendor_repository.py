import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repository.vendor import VendorRepository

class TestVendorRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.vendor_repo = VendorRepository(self.mock_connection)

    @patch('repository.vendor.db')
    def test_create_table(self, mock_db):
        # Execute
        self.vendor_repo.create_table()

        # Assert
        mock_db.create_tables.assert_called_once()
        args, _ = mock_db.create_tables.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("CREATE TABLE IF NOT EXISTS tbl_Vendors", args[1])

    @patch('repository.vendor.db')
    def test_get_by_id(self, mock_db):
        # Setup
        vendor_id = 1
        expected_vendor = {'Vendor_ID': vendor_id, 'Business_Name': 'ACME'}
        mock_db.execute_read_query_dict.return_value = [expected_vendor]

        # Execute
        result = self.vendor_repo.get_by_id(vendor_id)

        # Assert
        self.assertEqual(result, expected_vendor)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"WHERE Vendor_ID = {vendor_id}", args[1])

    @patch('repository.vendor.db')
    def test_search(self, mock_db):
        # Setup
        term = "ACME"
        mock_db.execute_read_query_dict.return_value = [{'Vendor_ID': 1, 'Business_Name': 'ACME Corp'}]

        # Execute
        self.vendor_repo.search(term)

        # Assert
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"LIKE '%{term}%'", args[1])

    @patch('repository.vendor.db')
    def test_get_all(self, mock_db):
        # Setup
        mock_db.execute_read_query_dict.return_value = [{'Vendor_ID': 1}, {'Vendor_ID': 2}]

        # Execute
        self.vendor_repo.get_all()

        # Assert
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn("SELECT * FROM tbl_Vendors", args[1])

    @patch('repository.vendor.db')
    def test_insert(self, mock_db):
        # Execute
        self.vendor_repo.insert(1, "Name", "Cat", "First", "Last", "Pref", "555-1212", "Mobile", "Now", "Now", "Addr", "Email", "Web", "Notes")

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("INSERT INTO tbl_Vendors", args[1])
        self.assertIn("VALUES (1, \"Name\"", args[1])

    @patch('repository.vendor.db')
    def test_update(self, mock_db):
        # Execute
        self.vendor_repo.update(1, "Name", "Cat", "First", "Last", "Pref", "555-1212", "Mobile", "Addr", "Email", "Web", "Notes", "Later")

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("UPDATE tbl_Vendors SET", args[1])
        self.assertIn("WHERE Vendor_ID = 1", args[1])

    @patch('repository.vendor.db')
    def test_get_max_id(self, mock_db):
        # Setup
        mock_db.execute_read_query_dict.return_value = [{'MaxID': 100}]

        # Execute
        result = self.vendor_repo.get_max_id()

        # Assert
        self.assertEqual(result, 100)
        mock_db.execute_read_query_dict.assert_called_once()

if __name__ == '__main__':
    unittest.main()
