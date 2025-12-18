import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from repository.account import AccountRepository


class TestAccountRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.account_repo = AccountRepository(self.mock_connection)

    @patch("repository.account.db")
    def test_create_table(self, mock_db):
        # Execute
        self.account_repo.create_table()

        # Assert
        mock_db.create_tables.assert_called_once()
        args, _ = mock_db.create_tables.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("CREATE TABLE IF NOT EXISTS tbl_Accounts", args[1])

    @patch("repository.account.db")
    def test_get_by_id(self, mock_db):
        # Setup
        account_id = 10001
        expected_account = {"Account_ID": account_id, "Name": "Cash"}
        mock_db.execute_read_query_dict.return_value = [expected_account]

        # Execute
        result = self.account_repo.get_by_id(account_id)

        # Assert
        self.assertEqual(result, expected_account)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"WHERE Account_ID = {account_id}", args[1])

    @patch("repository.account.db")
    def test_get_by_type_prefix(self, mock_db):
        # Setup
        prefix = "10"
        mock_db.execute_read_query_dict.return_value = [
            {"Account_ID": 10001, "Name": "Cash"}
        ]

        # Execute
        self.account_repo.get_by_type_prefix(prefix)

        # Assert
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"LIKE '{prefix}%'", args[1])

    @patch("repository.account.db")
    def test_get_all(self, mock_db):
        # Setup
        mock_db.execute_read_query_dict.return_value = [
            {"Account_ID": 1},
            {"Account_ID": 2},
        ]

        # Execute
        self.account_repo.get_all()

        # Assert
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn("SELECT * FROM tbl_Accounts", args[1])

    @patch("repository.account.db")
    def test_insert(self, mock_db):
        # Execute
        self.account_repo.insert(
            10001,
            "Cash",
            "Notes",
            "Now",
            "Now",
            "Bank",
            "Checking",
            "Routing",
            "AcctNum",
        )

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("INSERT INTO tbl_Accounts", args[1])
        self.assertIn('VALUES (10001, "Cash"', args[1])

    @patch("repository.account.db")
    def test_update(self, mock_db):
        # Execute
        self.account_repo.update(
            10001,
            "Cash",
            "Notes",
            "Later",
            "Bank",
            "Checking",
            "Routing",
            "AcctNum",
        )

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("UPDATE tbl_Accounts SET", args[1])
        self.assertIn("WHERE Account_ID = 10001", args[1])

    @patch("repository.account.db")
    def test_get_count_in_range(self, mock_db):
        # Setup
        start = 10000
        end = 11000
        mock_db.execute_read_query_dict.return_value = [{"Number_of_Records": 5}]

        # Execute
        result = self.account_repo.get_count_in_range(start, end)

        # Assert
        self.assertEqual(result, 5)
        mock_db.execute_read_query_dict.assert_called_once()


if __name__ == "__main__":
    unittest.main()
