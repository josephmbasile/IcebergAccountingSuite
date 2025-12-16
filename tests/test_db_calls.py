import unittest
import sqlite3
import os
import sys

# Add parent directory to path to import db_calls
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db_calls

class TestDbCalls(unittest.TestCase):
    def setUp(self):
        # Use in-memory database for testing
        self.conn = db_calls.create_connection(':memory:')
        self.create_table_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id integer PRIMARY KEY,
                name text NOT NULL,
                email text
            );
        """
        db_calls.create_tables(self.conn, self.create_table_sql)

    def tearDown(self):
        db_calls.close_connection(self.conn)

    def test_create_connection(self):
        self.assertIsInstance(self.conn, sqlite3.Connection)

    def test_execute_query(self):
        insert_sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')"
        result = db_calls.execute_query(self.conn, insert_sql)
        self.assertEqual(result, "Query executed successfully")

    def test_execute_read_query(self):
        insert_sql = "INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')"
        db_calls.execute_query(self.conn, insert_sql)
        select_sql = "SELECT * FROM users WHERE name='Bob'"
        rows = db_calls.execute_read_query(self.conn, select_sql)
        self.assertIsNotNone(rows)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 'Bob')

    def test_execute_read_query_dict(self):
        insert_sql = "INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')"
        db_calls.execute_query(self.conn, insert_sql)
        select_sql = "SELECT * FROM users WHERE name='Charlie'"
        rows = db_calls.execute_read_query_dict(self.conn, select_sql)
        self.assertIsNotNone(rows)
        self.assertEqual(len(rows), 1)
        self.assertIsInstance(rows[0], dict)
        self.assertEqual(rows[0]['name'], 'Charlie')

    def test_execute_read_query_tuple(self):
        # This function sets row_factory to sqlite3.Row and does some zip magic
        insert_sql = "INSERT INTO users (name, email) VALUES ('David', 'david@example.com')"
        db_calls.execute_query(self.conn, insert_sql)
        select_sql = "SELECT * FROM users WHERE name='David'"
        rows = db_calls.execute_read_query_tuple(self.conn, select_sql)
        
        self.assertIsNotNone(rows)
        self.assertTrue(len(rows) > 0)
        
        # Based on analysis: results = tuple(zip(cursor.fetchall()))
        # rows is a list of tuples, where each tuple contains one element which is the Row object.
        first_row_wrapper = rows[0]
        self.assertIsInstance(first_row_wrapper, tuple)
        
        actual_row = first_row_wrapper[0]
        self.assertIsInstance(actual_row, sqlite3.Row)
        self.assertEqual(actual_row['name'], 'David')

    def test_error_handling(self):
        # Test executing invalid query
        result = db_calls.execute_query(self.conn, "SELECT * FROM non_existent_table")
        # execute_query returns the exception object on error
        self.assertIsInstance(result, sqlite3.Error)

    def test_load_db_to_memory(self):
        # Populate current in-memory db
        insert_sql = "INSERT INTO users (name, email) VALUES ('Eve', 'eve@example.com')"
        db_calls.execute_query(self.conn, insert_sql)
        
        # Load into a NEW memory connection
        new_conn = db_calls.load_db_to_memory(self.conn)
        
        self.assertNotEqual(self.conn, new_conn)
        
        # Verify data is present in new connection
        select_sql = "SELECT * FROM users WHERE name='Eve'"
        rows = db_calls.execute_read_query(new_conn, select_sql)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 'Eve')
        new_conn.close()

    def test_generate_filekey(self):
        # Use a temporary file path
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            db_name = "test_db.icb"
            # generate_filekey(db_name, save_location)
            # It appends '/' to save_location if missing
            key, filename = db_calls.generate_filekey(db_name, temp_dir)
            
            self.assertIsInstance(key, bytes)
            self.assertEqual(filename, "test_db.icbkey")
            
            expected_key_path = os.path.join(temp_dir, filename)
            self.assertTrue(os.path.exists(expected_key_path))
            
            with open(expected_key_path, 'rb') as f:
                content = f.read()
                self.assertEqual(content, key)
                
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
