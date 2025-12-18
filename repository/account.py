import logging
import db_calls as db

logger = logging.getLogger(__name__)


class AccountRepository:
    SCHEMA = """CREATE TABLE IF NOT EXISTS tbl_Accounts (
        Account_ID INTEGER NOT NULL,
        Name VARCHAR(9999) NOT NULL UNIQUE,
        Notes VARCHAR(9999),
        Created_Time VARCHAR(9999) NOT NULL,
        Edited_Time VARCHAR(9999) NOT NULL,
        Institution VARCHAR(9999),
        Ins_Account_Type VARCHAR(9999),
        Ins_Routing_Number VARCHAR(9999),
        Ins_Account_Number VARCHAR(9999),
        PRIMARY KEY ("Account_ID")
    );"""

    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        """
        Creates the tbl_Accounts table in the database.
        """
        logger.debug(f"create_table: Executing query: {self.SCHEMA}")
        return db.create_tables(self.connection, self.SCHEMA)

    def get_all(self):
        """
        Retrieves all accounts.
        """
        query = "SELECT * FROM tbl_Accounts;"
        logger.debug(f"get_all: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def get_by_id(self, account_id):
        """
        Retrieves an account by its Account_ID.
        """
        query = f"SELECT * FROM tbl_Accounts WHERE Account_ID = {account_id};"
        logger.debug(f"get_by_id: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)

        if result and len(result) > 0:
            return result[0]
        return None
    
    def get_by_type_prefix(self, prefix):
        """
        Retrieves accounts where Account_ID starts with the given prefix.
        This roughly corresponds to filtering by type (e.g. '10' for Assets).
        """
        query = f"SELECT * FROM tbl_Accounts WHERE CAST(Account_ID AS TEXT) LIKE '{prefix}%';"
        logger.debug(f"get_by_type_prefix: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def insert(
        self,
        account_id,
        name,
        notes,
        created_time,
        edited_time,
        institution,
        ins_account_type,
        ins_routing_number,
        ins_account_number,
    ):
        """
        Inserts a new account into the tbl_Accounts table.
        """
        query = f"""INSERT INTO tbl_Accounts (Account_ID, Name, Notes, Created_Time, Edited_Time, Institution, Ins_Account_Type, Ins_Routing_Number, Ins_Account_Number)
            VALUES ({account_id}, "{name}", "{notes}", "{created_time}", "{edited_time}", "{institution}", "{ins_account_type}", "{ins_routing_number}", "{ins_account_number}");"""
        logger.debug(f"insert: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def update(
        self,
        account_id,
        name,
        notes,
        edited_time,
        institution,
        ins_account_type,
        ins_routing_number,
        ins_account_number,
    ):
        """
        Updates an account.
        """
        query = f"""UPDATE tbl_Accounts SET Name = '{name}', Notes = '{notes}', Edited_Time = '{edited_time}', Institution = '{institution}', Ins_Account_Number = '{ins_account_number}', Ins_Account_Type = '{ins_account_type}', Ins_Routing_Number = '{ins_routing_number}' WHERE Account_ID = {account_id};"""
        logger.debug(f"update: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def get_count_in_range(self, start_id, end_id):
        """
        Counts accounts in a given ID range.
        Used for calculating new account numbers.
        """
        query = f"SELECT COUNT(Account_ID) AS Number_of_Records FROM tbl_Accounts WHERE Account_ID > {start_id} AND Account_ID < {end_id};"
        logger.debug(f"get_count_in_range: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)
        if result and len(result) > 0:
             return result[0]['Number_of_Records']
        return 0
