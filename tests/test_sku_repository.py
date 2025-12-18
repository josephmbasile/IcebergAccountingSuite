import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from repository.sku import SkuRepository


class TestSkuRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.sku_repo = SkuRepository(self.mock_connection)

    @patch("repository.sku.db")
    def test_create_table(self, mock_db):
        # Execute
        self.sku_repo.create_table()

        # Assert
        mock_db.create_tables.assert_called_once()
        args, _ = mock_db.create_tables.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("CREATE TABLE IF NOT EXISTS tbl_Skus", args[1])

    @patch("repository.sku.db")
    def test_get_by_sku(self, mock_db):
        # Setup
        sku_code = "SKU123"
        expected_sku = {"Sku": sku_code, "Description": "Test Item"}
        mock_db.execute_read_query_dict.return_value = [expected_sku]

        # Execute
        result = self.sku_repo.get_by_sku(sku_code)

        # Assert
        self.assertEqual(result, expected_sku)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"WHERE Sku = '{sku_code}'", args[1])

    @patch("repository.sku.db")
    def test_get_by_id(self, mock_db):
        # Setup
        sku_id = 123
        expected_sku = {"Sku_ID": sku_id, "Sku": "SKU123"}
        mock_db.execute_read_query_dict.return_value = [expected_sku]

        # Execute
        result = self.sku_repo.get_by_id(sku_id)

        # Assert
        self.assertEqual(result, expected_sku)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"WHERE Sku_ID = {sku_id}", args[1])

    @patch("repository.sku.db")
    def test_search(self, mock_db):
        # Setup
        term = "Test"
        mock_db.execute_read_query_dict.return_value = [{"Sku": "SKU1"}]

        # Execute
        self.sku_repo.search(term)

        # Assert
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"LIKE '%{term}%'", args[1])

    @patch("repository.sku.db")
    def test_get_services(self, mock_db):
        # Setup
        term = "Service"
        mock_db.execute_read_query_dict.return_value = [{"Sku": "SERV1"}]

        # Execute
        self.sku_repo.get_services(term)

        # Assert
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn("AND Inventory LIKE '%False%' AND Type LIKE '%Service%'", args[1])

    @patch("repository.sku.db")
    def test_insert(self, mock_db):
        # Execute
        self.sku_repo.insert(
            "SKU1", "Desc", "Long Desc", 100, "True", "False", "Service", "Now", "Now"
        )

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("INSERT INTO tbl_Skus", args[1])
        self.assertIn("VALUES('SKU1'", args[1])

    @patch("repository.sku.db")
    def test_update(self, mock_db):
        # Execute
        self.sku_repo.update("SKU1", "New Desc", "New Long Desc", 200, "False", "Later")

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("UPDATE tbl_Skus SET", args[1])
        self.assertIn("WHERE Sku = 'SKU1'", args[1])


if __name__ == "__main__":
    unittest.main()
