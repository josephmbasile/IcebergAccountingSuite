import logging
import db_calls as db

logger = logging.getLogger(__name__)


class VendorRepository:
    SCHEMA = """CREATE TABLE IF NOT EXISTS tbl_Vendors (
        Vendor_ID INTEGER NOT NULL,
        Business_Name VARCHAR(9999) NOT NULL UNIQUE,
        Merchant_Category VARCHAR(9999) NOT NULL,
        Contact_First_Name VARCHAR(9999) NOT NULL,
        Contact_Last_Name VARCHAR(9999) NOT NULL,
        Preferred_Name VARCHAR(9999) NOT NULL,
        Phone_Number VARCHAR(9999),
        Phone_Number_Type VARCHAR(9999),
        Created_Time VARCHAR(9999) NOT NULL,
        Edited_Time VARCHAR(9999) NOT NULL,
        Business_Address VARCHAR(9999),
        Business_Email VARCHAR(9999),
        Business_Website VARCHAR(9999),
        Notes VARCHAR(9999),
        PRIMARY KEY ("Vendor_ID")
    );"""

    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        """
        Creates the tbl_Vendors table in the database.
        """
        logger.debug(f"create_table: Executing query: {self.SCHEMA}")
        return db.create_tables(self.connection, self.SCHEMA)

    def get_all(self):
        """
        Retrieves all vendors.
        """
        query = "SELECT * FROM tbl_Vendors;"
        logger.debug(f"get_all: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def get_by_id(self, vendor_id):
        """
        Retrieves a vendor by its Vendor_ID.
        """
        query = f"SELECT * FROM tbl_Vendors WHERE Vendor_ID = {vendor_id};"
        logger.debug(f"get_by_id: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)

        if result and len(result) > 0:
            return result[0]
        return None

    def search(self, search_term):
        """
        Searches for vendors matching the search term.
        """
        query = f"SELECT * FROM tbl_Vendors WHERE Business_Name LIKE '%{search_term}%' OR Merchant_Category LIKE '%{search_term}%' OR Contact_First_Name LIKE '%{search_term}%' OR Contact_Last_Name LIKE '%{search_term}%' OR Preferred_Name LIKE '%{search_term}%' OR Business_Address LIKE '%{search_term}%' OR Business_Email LIKE '%{search_term}%' OR Business_Website LIKE '%{search_term}%' OR Notes LIKE '%{search_term}%' OR Phone_Number LIKE '%{search_term}%';"
        logger.debug(f"search: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def insert(
        self,
        vendor_id,
        business_name,
        merchant_category,
        contact_first_name,
        contact_last_name,
        preferred_name,
        phone_number,
        phone_number_type,
        created_time,
        edited_time,
        business_address,
        business_email,
        business_website,
        notes,
    ):
        """
        Inserts a new vendor into the tbl_Vendors table.
        """
        query = f"""INSERT INTO tbl_Vendors (Vendor_ID, Business_Name, Merchant_Category, Contact_First_Name, Contact_Last_Name, Preferred_Name, Phone_Number, Phone_Number_Type, Created_Time, Edited_Time, Business_Address, Business_Email, Business_Website, Notes)
            VALUES ({vendor_id}, "{business_name}", "{merchant_category}", "{contact_first_name}", "{contact_last_name}", "{preferred_name}", "{phone_number}", "{phone_number_type}", "{created_time}", "{edited_time}", "{business_address}", "{business_email}", "{business_website}", "{notes}");"""
        logger.debug(f"insert: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def update(
        self,
        vendor_id,
        business_name,
        merchant_category,
        contact_first_name,
        contact_last_name,
        preferred_name,
        phone_number,
        phone_number_type,
        business_address,
        business_email,
        business_website,
        notes,
        edited_time,
    ):
        """
        Updates a vendor.
        """
        query = f"""UPDATE tbl_Vendors SET Edited_Time = '{edited_time}', Business_Name = "{business_name}", Merchant_Category = "{merchant_category}", Contact_First_Name = "{contact_first_name}", Contact_Last_Name = "{contact_last_name}", Preferred_Name = "{preferred_name}", Phone_Number = '{phone_number}', Phone_Number_Type = '{phone_number_type}', Business_Address = "{business_address}", Business_Email = '{business_email}', Business_Website = '{business_website}', Notes = "{notes}" WHERE Vendor_ID = {vendor_id};"""
        logger.debug(f"update: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def get_max_id(self):
        """
        Gets the maximum Vendor_ID.
        """
        query = "SELECT MAX(Vendor_ID) as MaxID FROM tbl_Vendors;"
        logger.debug(f"get_max_id: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)
        if result and len(result) > 0 and "MaxID" in result[0]:
            return result[0]["MaxID"]
        return None
