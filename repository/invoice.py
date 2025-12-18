import logging
import db_calls as db

logger = logging.getLogger(__name__)


class InvoiceRepository:
    SCHEMA = """CREATE TABLE IF NOT EXISTS tbl_Invoices (
        Invoice_ID INTEGER NOT NULL,
        Customer_ID INT(16) NOT NULL,
        Tracking_Code VARCHAR(9999) NOT NULL,
        Line_Items VARCHAR(9999) NOT NULL,
        Due_Date DATE NOT NULL,
        Created_Time VARCHAR(9999) NOT NULL,
        Edited_Time VARCHAR(9999) NOT NULL,
        Subtotal INT(16) NOT NULL,
        Sales_Tax INT(16) NOT NULL,
        Total INT(16) NOT NULL,
        Status VARCHAR(6) NOT NULL,
        Payment_Method VARCHAR(9999) NOT NULL,
        Location VARCHAR(9999) NOT NULL,
        PRIMARY KEY ("Invoice_ID" AUTOINCREMENT)
    );"""

    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        """
        Creates the tbl_Invoices table in the database.
        """
        logger.debug(f"create_table: Executing query: {self.SCHEMA}")
        return db.create_tables(self.connection, self.SCHEMA)

    def get_all(self):
        """
        Retrieves all invoices.
        """
        query = "SELECT * FROM tbl_Invoices;"
        logger.debug(f"get_all: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def get_by_id(self, invoice_id):
        """
        Retrieves an invoice by its Invoice_ID.
        """
        query = f"SELECT * FROM tbl_Invoices WHERE Invoice_ID = {invoice_id};"
        logger.debug(f"get_by_id: Executing query: {query}")
        result = db.execute_read_query_dict(self.connection, query)

        if result and len(result) > 0:
            return result[0]
        return None

    def get_by_customer_id(self, customer_id):
        """
        Retrieves invoices for a specific customer.
        """
        query = f"SELECT * FROM tbl_Invoices WHERE Customer_ID = {customer_id};"
        logger.debug(f"get_by_customer_id: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def search(self, search_term):
        """
        Searches invoices by various fields.
        """
        query = f"""SELECT * FROM tbl_Invoices WHERE 
            Invoice_ID LIKE '%{search_term}%' OR 
            Customer_ID LIKE '%{search_term}%' OR 
            Tracking_Code LIKE '%{search_term}%' OR 
            Line_Items LIKE '%{search_term}%' OR 
            Subtotal LIKE '%{search_term}%' OR 
            Total LIKE '%{search_term}%' OR 
            Status LIKE '%{search_term}%' OR 
            Payment_Method LIKE '%{search_term}%';"""
        logger.debug(f"search: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)

    def insert(
        self,
        customer_id,
        tracking_code,
        line_items,
        due_date,
        created_time,
        edited_time,
        subtotal,
        sales_tax,
        total,
        status,
        payment_method,
        location,
        invoice_id=None
    ):
        """
        Inserts a new invoice. If invoice_id is provided, it uses it (though AutoIncrement usually handles this).
        """
        # Note: Handling Invoice_ID if passed, otherwise letting AutoIncrement work if it was excluded from INSERT cols.
        # However, the original code in iceberg.py explicitly inserts Invoice_ID in save_invoice_to_database.
        # "VALUES ({icb_session.this_invoice['Invoice_ID']}, ..."
        
        cols = "Customer_ID, Tracking_Code, Line_Items, Due_Date, Created_Time, Edited_Time, Subtotal, Sales_Tax, Total, Status, Payment_Method, Location"
        vals = f"{customer_id}, '{tracking_code}', '{line_items}', '{due_date}', '{created_time}', '{edited_time}', '{subtotal}', '{sales_tax}', '{total}', '{status}', '{payment_method}', '{location}'"
        
        if invoice_id is not None:
             cols = "Invoice_ID, " + cols
             vals = f"{invoice_id}, " + vals

        query = f"""INSERT INTO tbl_Invoices ({cols}) VALUES ({vals});"""
        logger.debug(f"insert: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def update(
        self,
        invoice_id,
        customer_id=None,
        tracking_code=None,
        line_items=None,
        due_date=None,
        edited_time=None,
        subtotal=None,
        sales_tax=None,
        total=None,
        status=None,
        payment_method=None,
        location=None
    ):
        """
        Updates an existing invoice. Only fields that are not None will be updated.
        """
        updates = []
        if customer_id is not None:
            updates.append(f"Customer_ID = {customer_id}")
        if tracking_code is not None:
            updates.append(f"Tracking_Code = '{tracking_code}'")
        if line_items is not None:
            updates.append(f"Line_Items = '{line_items}'")
        if due_date is not None:
            updates.append(f"Due_Date = '{due_date}'")
        if edited_time is not None:
            updates.append(f"Edited_Time = '{edited_time}'")
        if subtotal is not None:
            updates.append(f"Subtotal = '{subtotal}'")
        if sales_tax is not None:
            updates.append(f"Sales_Tax = '{sales_tax}'")
        if total is not None:
             updates.append(f"Total = '{total}'")
        if status is not None:
            updates.append(f"Status = '{status}'")
        if payment_method is not None:
            updates.append(f"Payment_Method = '{payment_method}'")
        if location is not None:
            updates.append(f"Location = '{location}'")
            
        if not updates:
            return "No fields to update"

        query = f"""UPDATE tbl_Invoices SET {', '.join(updates)} WHERE Invoice_ID = {invoice_id};"""
        logger.debug(f"update: Executing query: {query}")
        return db.execute_query(self.connection, query)

    def get_count(self):
        """
        Returns the total number of invoices.
        """
        query = "SELECT COUNT(*) FROM tbl_Invoices;"
        result = db.execute_read_query_dict(self.connection, query)
        if result and len(result) > 0:
            return result[0]['COUNT(*)']
        return 0

    def get_totals_by_customer_and_status(self, customer_id, statuses):
        """
        Retrieves 'Total' of invoices for a specific customer and list of statuses.
        statuses: list of strings, e.g. ['Due', 'Overdue']
        """
        if not statuses:
            return []
        
        status_conditions = " OR ".join([f"Status = '{s}'" for s in statuses])
        query = f"""SELECT Total FROM tbl_Invoices WHERE Customer_ID = {customer_id} AND ({status_conditions});"""
        logger.debug(f"get_totals_by_customer_and_status: Executing query: {query}")
        return db.execute_read_query_dict(self.connection, query)
