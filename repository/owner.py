import logging
import db_calls as db

logger = logging.getLogger(__name__)


class OwnerRepository:

    SCHEMA = """CREATE TABLE IF NOT EXISTS tbl_Owners (
        Owner_ID INTEGER NOT NULL,
        First_Name VARCHAR(9999) NOT NULL,
        Middle_Name VARCHAR(9999),
        Last_Name VARCHAR(9999) NOT NULL,
        Preferred_Name VARCHAR(9999) NOT NULL,
        Full_Name VARCHAR(9999) NOT NULL,
        Phone_Number VARCHAR(9999),
        Phone_Number_Type VARCHAR(9999),
        Created_Time VARCHAR(9999) NOT NULL,
        Edited_Time VARCHAR(9999) NOT NULL,
        Home_Address VARCHAR(9999),
        Record_Location VARCHAR(9999) NOT NULL,
        Email VARCHAR(9999),
        PRIMARY KEY ("Owner_ID" AUTOINCREMENT)
    );"""

    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        """
        Creates the tbl_Owners table in the database.
        """
        logger.debug(f"create_table: Executing query: {self.SCHEMA}")
        return db.create_tables(self.connection, self.SCHEMA)

    def get_all(self):
        """
        Retrieves all owners.
        """
        query = "SELECT * FROM tbl_Owners;"
        logger.debug(f"get_all: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def get_by_id(self, owner_id):
        """
        Retrieves an owner by their Owner_ID.
        """
        query = f"SELECT * FROM tbl_Owners WHERE Owner_ID = {owner_id};"
        logger.debug(f"get_by_id: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)

        if result and len(result) > 0:
            return result[0]
        return None

    def insert(
        self,
        first_name,
        last_name,
        preferred_name,
        full_name,
        created_time,
        edited_time,
        record_location,
        middle_name=None,
        phone_number=None,
        phone_number_type=None,
        home_address=None,
        email=None
    ):
        """
        Inserts a new owner into the tbl_Owners table.
        """
        # Helper to handle None values for optional fields
        def fmt(val):
            return f"{val}" if val is not None else ""

        query = f"""INSERT INTO tbl_Owners (First_Name, Middle_Name, Last_Name, Preferred_Name, Full_Name, Phone_Number, Phone_Number_Type, Created_Time, Edited_Time, Home_Address, Record_Location, Email)
            VALUES("{first_name}", "{fmt(middle_name)}", "{last_name}", "{preferred_name}", "{full_name}", "{fmt(phone_number)}", "{fmt(phone_number_type)}", "{created_time}", "{edited_time}", "{fmt(home_address)}", "{record_location}", "{fmt(email)}");"""
        logger.debug(f"insert: Executing query: {query}")
        return db.execute_query(self.connection, query)
