import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from repository.owner import OwnerRepository

class TestOwnerRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.repo = OwnerRepository(self.mock_connection)

    @patch("repository.owner.db")
    def test_create_table(self, mock_db):
        self.repo.create_table()
        mock_db.create_tables.assert_called_once()
        args, _ = mock_db.create_tables.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("CREATE TABLE IF NOT EXISTS tbl_Owners", args[1])

    @patch("repository.owner.db")
    def test_get_all(self, mock_db):
        mock_db.execute_read_query_dict.return_value = [{"Owner_ID": 1}]
        result = self.repo.get_all()
        self.assertEqual(len(result), 1)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn("SELECT * FROM tbl_Owners;", args[1])

    @patch("repository.owner.db")
    def test_get_by_id(self, mock_db):
        mock_db.execute_read_query_dict.return_value = [{"Owner_ID": 1}]
        result = self.repo.get_by_id(1)
        self.assertEqual(result["Owner_ID"], 1)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn("WHERE Owner_ID = 1", args[1])

    @patch("repository.owner.db")
    def test_insert(self, mock_db):
        self.repo.insert(
            first_name="John",
            middle_name="Q",
            last_name="Doe",
            preferred_name="Johnny",
            full_name="John Q Doe",
            phone_number="555-1212",
            phone_number_type="Mobile",
            created_time="Now",
            edited_time="Later",
            home_address="123 Main St",
            record_location="Office",
            email="john@example.com"
        )
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("INSERT INTO tbl_Owners", args[1])
        # Verify columns are correct based on the schema and input
        self.assertIn("First_Name", args[1])
        self.assertIn("Middle_Name", args[1])
        self.assertIn("Last_Name", args[1])
        self.assertIn("VALUES", args[1])
        self.assertIn('"John"', args[1])
        self.assertIn('"Q"', args[1])
        self.assertIn('"Doe"', args[1])

if __name__ == "__main__":
    unittest.main()
