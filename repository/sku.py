import logging
import db_calls as db

logger = logging.getLogger(__name__)


class SkuRepository:
    SCHEMA = """CREATE TABLE IF NOT EXISTS tbl_Skus (
        Sku_ID INTEGER NOT NULL,
        Sku VARCHAR(24) NOT NULL UNIQUE,
        Created_Time VARCHAR(9999) NOT NULL,
        Edited_Time VARCHAR(9999) NOT NULL,
        Description VARCHAR(9999) NOT NULL,
        Long_Description VARCHAR(9999) NOT NULL,
        Price INT(16) NOT NULL,
        Taxable VARCHAR(9999) NOT NULL,
        Inventory VARCHAR(9999) NOT NULL,
        Type VARCHAR(9999) NOT NULL,
        PRIMARY KEY ("Sku_ID" AUTOINCREMENT)
    );"""

    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        """
        Creates the tbl_Skus table in the database.
        """
        logger.debug(f"create_table: Executing query: {self.SCHEMA}")
        return db.create_tables(self.connection, self.SCHEMA)

    def get_by_sku(self, sku):
        """
        Retrieves a SKU by its Sku string identifier.
        """
        query = f"SELECT * FROM tbl_Skus WHERE Sku = '{sku}';"
        logger.debug(f"get_by_sku: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)
        
        if result and len(result) > 0:
            return result[0]
        return None

    def get_by_id(self, sku_id):
        """
        Retrieves a SKU by its Sku_ID.
        """
        query = f"SELECT * FROM tbl_Skus WHERE Sku_ID = {sku_id};"
        logger.debug(f"get_by_id: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)
        
        if result and len(result) > 0:
            return result[0]
        return None

    def search(self, search_term):
        """
        Searches for SKUs matching the search term.
        """
        query = f"SELECT * FROM tbl_Skus WHERE Sku_ID LIKE '%{search_term}%' OR Sku LIKE '%{search_term}%' OR Description LIKE '%{search_term}%' OR Long_Description LIKE '%{search_term}%';"
        logger.debug(f"search: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def get_services(self, search_term):
        """
        Retrieves services matching the search term.
        """
        query = f"SELECT * FROM tbl_Skus WHERE (Sku LIKE '%{search_term}%' OR Description LIKE '%{search_term}%' OR Long_Description LIKE '%{search_term}%' OR Price LIKE '%{search_term}%' OR Taxable LIKE '%{search_term}%') AND Inventory LIKE '%False%' AND Type LIKE '%Service%';"
        logger.debug(f"get_services: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def insert(self, sku, description, long_description, price, taxable, inventory, type, created_time, edited_time):
        """
        Inserts a new SKU into the tbl_Skus table.
        """
        query = f"INSERT INTO tbl_Skus (Sku, Description, Long_Description, Price, Taxable, Inventory, Type, Created_Time, Edited_Time) VALUES('{sku}', '{description}', '{long_description}', {price}, '{taxable}', '{inventory}', '{type}', '{created_time}', '{edited_time}');"
        logger.debug(f"insert: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def update(self, sku, description, long_description, price, taxable, edited_time):
        """
        Updates a SKU.
        """
        query = f"UPDATE tbl_Skus SET Edited_Time = '{edited_time}', Description = \"{description}\", Long_Description = \"{long_description}\", Price = {price}, Taxable = '{taxable}' WHERE Sku = '{sku}';"
        logger.debug(f"update: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def get_max_sku(self):
        """
        Gets the maximum SKU string.
        """
        query = "SELECT MAX(Sku) as MaxSku FROM tbl_Skus;"
        logger.debug(f"get_max_sku: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)
        if result and len(result) > 0 and 'MaxSku' in result[0]:
            return result[0]['MaxSku']
        return None
