import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repository.property import PropertyRepository

class TestPropertyRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.property_repo = PropertyRepository(self.mock_connection)

    @patch('repository.property.db')
    def test_create_table(self, mock_db):
        # Execute
        self.property_repo.create_table()

        # Assert
        mock_db.create_tables.assert_called_once()
        args, _ = mock_db.create_tables.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("CREATE TABLE IF NOT EXISTS tbl_Properties", args[1])

    @patch('repository.property.db')
    def test_get_found(self, mock_db):
        # Setup
        property_name = "Business Name"
        expected_value = "Test Corp"
        mock_db.execute_read_query_dict.return_value = [{'Property_Value': expected_value}]

        # Execute
        result = self.property_repo.get(property_name)

        # Assert
        self.assertEqual(result, expected_value)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn(f"WHERE Property_Name IS '{property_name}'", args[1])

    @patch('repository.property.db')
    def test_get_not_found(self, mock_db):
        # Setup
        mock_db.execute_read_query_dict.return_value = []

        # Execute
        result = self.property_repo.get("NonExistent")

        # Assert
        self.assertIsNone(result)

    @patch('repository.property.db')
    def test_insert(self, mock_db):
        # Setup
        property_name = "New Prop"
        property_value = "Value"
        property_units = "Units"
        created_time = "2023-01-01"
        edited_time = "2023-01-01"

        # Execute
        self.property_repo.insert(property_name, property_value, property_units, created_time, edited_time)

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("INSERT INTO tbl_Properties", args[1])
        self.assertIn(f"VALUES('{property_name}'", args[1])

    @patch('repository.property.db')
    def test_update(self, mock_db):
        # Setup
        property_name = "Business Name"
        new_value = "New Corp"
        edited_time = "2023-01-02"
        
        # Execute
        self.property_repo.update(property_name, new_value, edited_time)

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn(f"UPDATE tbl_Properties SET Property_Value = '{new_value}'", args[1])
        self.assertIn(f"WHERE Property_Name = '{property_name}'", args[1])

if __name__ == '__main__':
    unittest.main()
