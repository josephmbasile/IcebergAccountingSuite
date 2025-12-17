import logging
import db_calls as db

logger = logging.getLogger(__name__)


class PropertyRepository:
    SCHEMA = """CREATE TABLE IF NOT EXISTS tbl_Properties (
        Property_ID INTEGER NOT NULL,
        Property_Name VARCHAR(9999) NOT NULL,
        Property_Value VARCHAR(9999) NOT NULL,
        Property_Units VARCHAR(9999) NOT NULL, 
        Created_Time VARCHAR(9999) NOT NULL,
        Edited_Time VARCHAR(9999) NOT NULL,
        PRIMARY KEY ("Property_ID" AUTOINCREMENT)
    );"""

    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        """
        Creates the tbl_Properties table in the database.
        """
        logger.debug(f"create_table: Executing query: {self.SCHEMA}")
        return db.create_tables(self.connection, self.SCHEMA)

    def get(self, property_name):
        """
        Retrieves the value of a specific property from the tbl_Properties table.
        Returns the value if found, otherwise returns None.
        """
        query = f"SELECT Property_Value FROM tbl_Properties WHERE Property_Name IS '{property_name}';"
        logger.debug(f"get: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)
        
        if result and len(result) > 0 and 'Property_Value' in result[0]:
            return result[0]['Property_Value']
        return None

    def insert(self, property_name, property_value, property_units, created_time, edited_time):
        """
        Inserts a new property into the tbl_Properties table.
        """
        query = f"""INSERT INTO tbl_Properties (Property_Name, Property_Value, Property_Units, Created_Time, Edited_Time)
            VALUES('{property_name}', '{property_value}', '{property_units}', '{created_time}', '{edited_time}');"""
        logger.debug(f"insert: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def update(self, property_name, property_value, edited_time):
        """
        Updates the value of a specific property in the tbl_Properties table.
        """
        query = f"UPDATE tbl_Properties SET Property_Value = '{property_value}', Edited_Time = '{edited_time}' WHERE Property_Name = '{property_name}';"
        logger.debug(f"update: Executing query: {query}")
        return db.execute_query(self.connection, query)
