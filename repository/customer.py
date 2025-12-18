import logging
import db_calls as db

logger = logging.getLogger(__name__)


class CustomerRepository:
    SCHEMA = """CREATE TABLE IF NOT EXISTS tbl_Customers (
        Customer_ID INTEGER NOT NULL,
        Customer_First_Name VARCHAR(9999) NOT NULL,
        Customer_Last_Name VARCHAR(9999) NOT NULL,
        Customer_Company_Name VARCHAR(9999),
        Customer_Retail_Certificate VARCHAR(9999),
        Preferred_Name VARCHAR(9999) NOT NULL,
        Customer_Phone_Number VARCHAR(9999),
        Customer_Phone_Number_Type VARCHAR(9999),
        Created_Time VARCHAR(9999) NOT NULL,
        Edited_Time VARCHAR(9999) NOT NULL,
        Customer_Address VARCHAR(9999),
        Customer_Email VARCHAR(9999),
        Notes VARCHAR(9999),
        PRIMARY KEY ("Customer_ID" AUTOINCREMENT)
    );"""

    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        """
        Creates the tbl_Customers table in the database.
        """
        logger.debug(f"create_table: Executing query: {self.SCHEMA}")
        return db.create_tables(self.connection, self.SCHEMA)

    def get_by_id(self, customer_id):
        """
        Retrieves a customer by their Customer_ID.
        """
        query = f"SELECT * FROM tbl_Customers WHERE Customer_ID = {customer_id};"
        logger.debug(f"get_by_id: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)
        
        if result and len(result) > 0:
            return result[0]
        return None

    def search(self, search_term):
        """
        Searches customers by various fields.
        """
        query = f"""SELECT * FROM tbl_Customers WHERE 
            Customer_First_Name LIKE '%{search_term}%' OR 
            Customer_Last_Name LIKE '%{search_term}%' OR 
            Customer_Company_Name LIKE '%{search_term}%' OR 
            Preferred_Name LIKE '%{search_term}%' OR 
            Customer_Phone_Number LIKE '%{search_term}%' OR 
            Customer_Email LIKE '%{search_term}%' OR 
            Customer_Address LIKE '%{search_term}%' OR
            Notes LIKE '%{search_term}%';"""
        logger.debug(f"search: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def insert(
        self,
        customer_id,
        company_name,
        first_name,
        last_name,
        preferred_name,
        phone,
        phone_type,
        created_time,
        edited_time,
        address,
        email,
        notes,
        retail_certificate=""
    ):
        """
        Inserts a new customer.
        """
        cols = "Customer_ID, Customer_Company_Name, Customer_First_Name, Customer_Last_Name, Preferred_Name, Customer_Phone_Number, Customer_Phone_Number_Type, Created_Time, Edited_Time, Customer_Address, Customer_Email, Notes"
        vals = f"{customer_id}, '{company_name}', '{first_name}', '{last_name}', '{preferred_name}', '{phone}', '{phone_type}', '{created_time}', '{edited_time}', '{address}', '{email}', '{notes}'"
        
        # Add Retail Certificate if it exists (it was in schema but seemingly missing from some raw queries, adding for completeness if needed later)
        if retail_certificate:
             cols += ", Customer_Retail_Certificate"
             vals += f", '{retail_certificate}'"

        query = f"""INSERT INTO tbl_Customers ({cols}) VALUES ({vals});"""
        logger.debug(f"insert: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def update(
        self,
        customer_id,
        company_name=None,
        first_name=None,
        last_name=None,
        preferred_name=None,
        phone=None,
        phone_type=None,
        address=None,
        email=None,
        notes=None,
        edited_time=None
    ):
        """
        Updates an existing customer.
        """
        updates = []
        if company_name is not None:
            updates.append(f"Customer_Company_Name = '{company_name}'")
        if first_name is not None:
            updates.append(f"Customer_First_Name = '{first_name}'")
        if last_name is not None:
            updates.append(f"Customer_Last_Name = '{last_name}'")
        if preferred_name is not None:
            updates.append(f"Preferred_Name = '{preferred_name}'")
        if phone is not None:
            updates.append(f"Customer_Phone_Number = '{phone}'")
        if phone_type is not None:
            updates.append(f"Customer_Phone_Number_Type = '{phone_type}'")
        if address is not None:
            updates.append(f"Customer_Address = '{address}'")
        if email is not None:
            updates.append(f"Customer_Email = '{email}'")
        if notes is not None:
            updates.append(f"Notes = '{notes}'")
        if edited_time is not None:
            updates.append(f"Edited_Time = '{edited_time}'")

        if not updates:
            return "No fields to update"

        query = f"""UPDATE tbl_Customers SET {', '.join(updates)} WHERE Customer_ID = {customer_id};"""
        logger.debug(f"update: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def get_max_id(self):
        """
        Returns the maximum Customer_ID.
        """
        query = "SELECT MAX(Customer_ID) FROM tbl_Customers;"
        result = db.execute_read_query_dict(self.connection, query)
        if result and result[0]['MAX(Customer_ID)']:
             return int(result[0]['MAX(Customer_ID)'])
        return 0
