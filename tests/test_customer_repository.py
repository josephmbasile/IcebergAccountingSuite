import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from repository.customer import CustomerRepository


class TestCustomerRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock()
        self.customer_repo = CustomerRepository(self.mock_connection)

    @patch("repository.customer.db")
    def test_create_table(self, mock_db):
        # Execute
        self.customer_repo.create_table()

        # Assert
        mock_db.create_tables.assert_called_once()
        args, _ = mock_db.create_tables.call_args
        self.assertEqual(args[0], self.mock_connection)
        self.assertIn("CREATE TABLE IF NOT EXISTS tbl_Customers", args[1])

    @patch("repository.customer.db")
    def test_get_by_id(self, mock_db):
        # Setup
        customer_id = 1
        expected_customer = {"Customer_ID": customer_id, "Customer_First_Name": "John"}
        mock_db.execute_read_query_dict.return_value = [expected_customer]

        # Execute
        result = self.customer_repo.get_by_id(customer_id)

        # Assert
        self.assertEqual(result, expected_customer)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"WHERE Customer_ID = {customer_id}", args[1])

    @patch("repository.customer.db")
    def test_search(self, mock_db):
        # Setup
        search_term = "Doe"
        expected_customers = [{"Customer_First_Name": "John", "Customer_Last_Name": "Doe"}]
        mock_db.execute_read_query_dict.return_value = expected_customers

        # Execute
        result = self.customer_repo.search(search_term)

        # Assert
        self.assertEqual(result, expected_customers)
        mock_db.execute_read_query_dict.assert_called_once()
        args, _ = mock_db.execute_read_query_dict.call_args
        self.assertIn(f"LIKE '%{search_term}%'", args[1])

    @patch("repository.customer.db")
    def test_insert(self, mock_db):
        # Execute
        self.customer_repo.insert(
            customer_id=1,
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            preferred_name="Johnny",
            phone="555-0199",
            phone_type="Work",
            created_time="2023-01-01",
            edited_time="2023-01-01",
            address="123 Main St",
            email="john@example.com",
            notes="Standard customer"
        )

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("INSERT INTO tbl_Customers", args[1])
        self.assertIn("'Acme Corp'", args[1])

    @patch("repository.customer.db")
    def test_update(self, mock_db):
        # Execute
        self.customer_repo.update(
            customer_id=1,
            company_name="New Corp",
            edited_time="2023-02-01"
        )

        # Assert
        mock_db.execute_query.assert_called_once()
        args, _ = mock_db.execute_query.call_args
        self.assertIn("UPDATE tbl_Customers SET", args[1])
        self.assertIn("Customer_Company_Name = 'New Corp'", args[1])
        self.assertIn("WHERE Customer_ID = 1", args[1])
    
    @patch("repository.customer.db")
    def test_get_max_id(self, mock_db):
        # Setup
        mock_db.execute_read_query_dict.return_value = [{'MAX(Customer_ID)': 100}]
        
        # Execute
        max_id = self.customer_repo.get_max_id()
        
        # Assert
        self.assertEqual(max_id, 100)
        mock_db.execute_read_query_dict.assert_called_once()


if __name__ == "__main__":
    unittest.main()
