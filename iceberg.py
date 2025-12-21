import PySimpleGUI  as sg

import ast
import re
import db_calls as db
import datetime
from dateutil import parser
#import numpy as np
#import matplotlib.pyplot as plt
import time
from decimal import Decimal as dec
import tempfile
#import PIL
import shutil
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from cryptography.fernet import Fernet

import os
import sys
sys.path.append('PATH')
from tkinter import *
from PIL import ImageTk, Image
import string

from PIL import ImageDraw, ImageFont
import img2pdf
import subprocess
from iceberg_utils import get_current_time_info, format_currency, convert_dollars_to_cents, id_generator
import logging

from repository import PropertyRepository, VendorRepository, SkuRepository, AccountRepository, InvoiceRepository, CustomerRepository
from repository import OwnerRepository


#logging.basicConfig(level=logging.DEBUG)
#------------------------------------------Section 1 Date Information

sample_date = parser.parse('2023-04-02')

now= datetime.datetime.now()
current_date = now.date()
current_year = now.year
week_past = current_date - datetime.timedelta(6)


#------------------------------------------Section 2 Load Initial Data


#Instantiate a class for the session
class new_session:
    def __init__(self):
        self.current_time_display = get_current_time_info()
        self.ledger_name = ""#
        self.synchronized = "No"#
        self.connection = False#
        self.num = 1#
        self.guitimer="Initializing" ##
        #print(self.guitimer)
        self.db_name = ""#
        self.filekey = ""#
        self.filename = ""#
        self.database_loaded = False
        self.vendor_number = int(0)
        self.save_location = False#
        self.account_number = False
        self.window = False
        self.vendors = []
        self.transactions = []
        self.transaction_date = datetime.datetime.now()
        self.all_accounts = []
        self.current_date = f"{datetime.datetime.now().year}/{datetime.datetime.now().month}/{datetime.datetime.now().day}"
        self.business_name = []
        self.business_address = []
        self.owner_name = []
        self.owner_title = []
        self.owner_phone = []
        self.owner_email = []
        self.owner_notes = []
        self.business_ein = []
        self.customers= []
        self.current_year = now.year
        self.receipts_location = "."
        self.current_console_messages = [f"""Welcome to Iceberg Accounting Suite! Create or open a database to get started."""]
        self.session_filekey, self.session_filename, self.session_save_location= db.encrypt_database("sessions.icbs","decrypt","sessions.icbskey",False,"sessions.icbs")
        session_log_connection = db.create_connection("sessions.icbs")
        self.session_log_connection = db.load_db_to_memory(session_log_connection)
        self.session_filekey, self.session_filename, self.session_save_location= db.encrypt_database("sessions.icbs","encrypt","sessions.icbskey",False,"sessions.icbs")
        self.customer_number = 0
        #print(self.session_filekey)
        self.invoices= []  
        self.service_number = 0
        self.services = []
        self.transaction = ""
        self.these_customers = []
        self.these_skus = []
        self.sales_tax = 0.00
        self.these_line_items = []
        self.this_invoice = {"Invoice_ID":"","Line_Items":"", "Tracking_Code":"",
                             "Customer_ID":"","Subtotal": "", "Sales_Tax":"",
                             "Total":"","Status":"","Payment_Method":"","Location":"", "Due_Date": ""}
        self.transaction_debit_account = ""

    def console_log(self, message, current_console_messages):#
        """Posts a message to the console and logs it in the database.."""
        self.current_time_display = get_current_time_info()
        this_message = f"""Console ({self.current_time_display[1]}): {message}"""
        full_message = f"""{this_message}"""
        for i in range(len(current_console_messages)):
            full_message = full_message + f"""\n{current_console_messages[i]}"""
        
        self.window["-Console_Log-"].update(full_message)
        current_console_messages = [this_message] + current_console_messages           

        

        insert_log_entry_query = f"""INSERT INTO tbl_Console_Log (Console_Messages, Created_Time, Edited_Time)
            VALUES(("{this_message}"),("{self.current_time_display[1]}"),("{self.current_time_display[1]}"));
        """
        created_session_entry = db.execute_query(self.session_log_connection,insert_log_entry_query)
        full_message = full_message + f"""\nConsole ({self.current_time_display[0]}): {created_session_entry}"""

        if self.connection:     
            insert_log_entry_query = f"""INSERT INTO tbl_Console_Log (Console_Messages, Created_Time, Edited_Time)
                VALUES(("{this_message}"),("{self.current_time_display[1]}"),("{self.current_time_display[1]}"));
            """
            created_entry = db.execute_query(self.connection,insert_log_entry_query)
            full_message = full_message + f"""\nConsole ({self.current_time_display[0]}): {created_entry}"""
        return current_console_messages

icb_session = new_session()
print(icb_session.transaction_date)
print(icb_session.current_date)
#print(icb_session.guitimer)

#Set fixed variables

logo = "Logo_AI.png"

phone_types = ["Mobile","Home", "Office", "Work", "Other"]

account_types = [[0,"Assets"],[1,"Expenses"],[2,"Equity Withdrawals"],[3,"Liabilities"],[4,"Owner Equity"],[5,"Revenue"]]
bank_account_types = [[0,"Checking"],[1,"Savings"],[2,"Passbook"],[3,"Certificate of Deposit"]]

small_print = 8
medium_print = 11
large_print = 16
extra_large_print = 24
detailed_information_color="#dcfffe"
overview_information_color = "#bbf0f9"

#financials (SAMPLE DATA)
total_credits = "$0.00"
total_debits = "$0.00"
total_assets = "$0.00"
total_expenses = "$0.00"
total_equity_withdrawals = "$0.00"
total_liabilities = "$0.00"
owner_equity = "$0.00"
total_revenue = "$0.00"
net_assets = "$0.00"
total_equity = "$0.00"
retained_earnings = "$0.00"
business_income = "$0.00"

#------------------------------------------Section 3 GUI Layout

sg.theme('LightBlue3')

#import psutil


index = 0


#░▒▓█▓▒░         ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓████████▓▒░ 
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓████████▓▒░  ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓████████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░      ░▒▓██████▓▒░   ░▒▓██████▓▒░     ░▒▓█▓▒░     
                                                                                     

menu_def = [
    ['&File',['&New Database','&Open Database','!&Save Database','!Database &Properties','E&xit Iceberg']],
    ['&Dashboard',['!&Go to Dashboard']],
    ['&Ledger',['!&View Ledger','!&New Transaction']],
    ['&Reports',['!&Profit and Loss', '!Profit and Loss by &Month','!&Quarterly Report']],
    ['&Vendors',['!&View Vendors', '!&New Vendor']],
    ['&Customers',['!&View Customers', '!&New Customer','!&Point of Sale']],
    ['&Products',['!&View Products','!&New Product','!New &Lot']],
    ['&Services',['!&View Services','!&New Service']],
    ['&Help',['&Documentation', '&About']]
]

menu_def_2 = [
    ['&File',['&New Database','&Open Database','&Save Database','Database &Properties','E&xit Iceberg']],
    ['&Dashboard',['&Go to Dashboard']],
    ['&Ledger',['&View Ledger','&New Transaction']],
    ['&Reports',['!&Profit and Loss', '!Profit and Loss by &Month','!&Quarterly Report']],
    ['&Vendors',['&View Vendors', '&New Vendor']],
    ['&Customers',['&View Customers', '&New Customer','&Point of Sale']],
    ['&Products',['!&View Products','!&New Product','!New &Lot']],
    ['&Services',['&View Services','&New Service']],
    ['&Help',['&Documentation', '&About']]
]
account_information_labels_width = 20

edit_account_border_width = 0

view_account_labels_pad = 2


#-----------------Dashboard Setup----------------

balance_frame_layout = [
    [sg.Text(f"""Credits: {total_credits}; Debits: {total_debits}""", size=(35,1), font=("",small_print), enable_events=True, key="-Balance_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""Your records are balanced.""", size=(35,1), font=("",small_print), enable_events=True, key="-Balance_Message-", justification="center", background_color=overview_information_color)],
]

assets_frame_layout = [
    [sg.Text(f"""Total Assets: {total_assets}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Assets_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""Total Assets must equal Liabilities plus Total Equity.""", size=(35,2), font=("",small_print), enable_events=True, key="-Assets_Message-", justification="center", background_color=overview_information_color)],
]
expenses_frame_layout = [
    [sg.Text(f"""Total Expenses: {total_expenses}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Expenses_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""""", size=(35,1), font=("",small_print), enable_events=True, key="-Expenses_Message-", justification="center", background_color=overview_information_color)],
]
withdrawals_frame_layout = [
    [sg.Text(f"""Total Withdrawals: {total_equity_withdrawals}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Withdrawals_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""""", size=(35,1), font=("",small_print), enable_events=True, key="-Withdrawals_Message-", justification="center", background_color=overview_information_color)],
]
liabilities_frame_layout = [
    [sg.Text(f"""Total Liabilities: {total_liabilities}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Liabilities_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""""", size=(35,1), font=("",small_print), enable_events=True, key="-Liabilities_Message-", justification="center", background_color=overview_information_color)],
]
equity_frame_layout = [
    [sg.Text(f"""Owner_Equity: {owner_equity}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Equity_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""""", size=(35,1), font=("",small_print), enable_events=True, key="-Equity_Message-", justification="center", background_color=overview_information_color)],
]
revenue_frame_layout = [
    [sg.Text(f"""Revenue: {total_revenue}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Revenue_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""""", size=(35,1), font=("",small_print), enable_events=True, key="-Revenue_Message-", justification="center", background_color=overview_information_color)],
]
net_assets_frame_layout = [
    [sg.Text(f"""Net Assets: {net_assets}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Net_Assets_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""Net Assets must match Total Equity. \nTotal Assets - Liabilities""", size=(35,2), font=("",small_print), enable_events=True, key="-Net_Assets_Message-", justification="center", background_color=overview_information_color)],
]
total_equity_frame_layout = [
    [sg.Text(f"""Total Equity: {total_equity}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Total_Equity_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""Total Equity must match Net Assets. \nDeposits + Revenue - Expenses - Withdrawals""", size=(42,2), font=("",7), enable_events=True, key="-Total_Equity_Message-", justification="center", background_color=overview_information_color)],
]

retained_earnings_frame_layout = [
    [sg.Text(f"""Retained Earnings: {retained_earnings}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Retained_Earnings_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""Ordinary Business Income - Withdrawals""", size=(35,1), font=("",small_print), enable_events=True, key="-Retained_Earnings_Message-", justification="center", background_color=overview_information_color)],
]
business_income_frame_layout = [
    [sg.Text(f"""Business Income: {business_income}""", size=(27,1), font=("",medium_print), enable_events=True, key="-Business_Income_Report-", justification="center", background_color=overview_information_color)],
    [sg.Text(f"""""", size=(35,1), font=("",small_print), enable_events=True, key="-Business_Income_Message-", justification="center", background_color=overview_information_color)],
]

dashboard_column_layout = [
    [sg.Frame("",layout=assets_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=liabilities_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=net_assets_frame_layout, background_color=overview_information_color)], 
    [sg.Frame("",layout=revenue_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=expenses_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=business_income_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=withdrawals_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=retained_earnings_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=equity_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",layout=total_equity_frame_layout, background_color=overview_information_color)],
    [sg.Frame("",size=(234,80),layout=balance_frame_layout, background_color=overview_information_color)],
]

#Create the chart of accounts display
icb_session.db_name = "Select or Create Database"
chart_of_accounts_text_layout = [
    [sg.Table(values=[],row_height=36, bind_return_key=True, col_widths=[10,32,12,12,12], cols_justification=["c","c","c","c","c"], auto_size_columns=False, headings=["Account_ID", "Name", "Credits", "Debits", "Balance"], num_rows=25, expand_x=True, expand_y=True, font=("",medium_print), enable_events=False, justification="Center", key="-Chart_of_Accounts_Content-", background_color=detailed_information_color)],
]

database_years = ["All Years"]


chart_of_accounts_frame_layout = [
    [sg.Text(f"""{icb_session.db_name}:\n Chart of Accounts""", size=(50,2), justification = "center", expand_x = True, expand_y=True,  font=("",medium_print), enable_events=True, key="-Chart_Of_Accounts_Header-")],
    #[sg.Column([[]],element_justification="center", justification="center")],
    [sg.Frame(f"""""", layout=chart_of_accounts_text_layout, expand_x = True, expand_y=True, key="-Chart_Of_Accounts_Content_Frame-", size=(940,600), element_justification="Center", background_color=overview_information_color)],
    [sg.Push(),sg.Combo(values=database_years,enable_events=True, auto_size_text=True, default_value="All Years",key="-Account_Year_Picker-"), sg.Combo(values=["All Accounts","10 Assets","11 Expenses", "12 Withdrawals", "13 Liabilities", "14 Owner Equity", "15 Revenue"],enable_events=True, auto_size_text=True, default_value="All Accounts",key="-Account_Type_Picker-"), sg.Button("View Account", key="-View_Account_Button-", disabled=False), sg.Button("New Account", key="-New_Account_Button-", disabled=False)],
#expand_x = True, expand_y=True,
]

dashboard_column_layout_2 = [
    [sg.Column(chart_of_accounts_frame_layout, size= (900,720), expand_x=True, expand_y=True)]
]

#TODO: Create the default chart of accounts

#-----------------TABS----------------


dashboard_tab = [
    [sg.Column(dashboard_column_layout),sg.Column(dashboard_column_layout_2, expand_x=True, expand_y=True)],
]

#ledger_year_picker_column_layout = [
#        [sg.Text("Year: ", font=("",large_print), size=(14,1)), sg.OptionMenu(values=["CY2024","CY2023"], auto_size_text=True, default_value="CY2024",key="-Ledger_Year_Picker-")],
#]

reports_tab = [
    [sg.Text(font=("",medium_print), size=(133,1))],
    [sg.Text("Reports")],
]


view_vendors_data_height = 30
view_vendors_labels_width = 10
view_vendors_data_width = 30

view_vendors_edit_layout = [
    #[sg.Text(f"",font=("",2), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"No Vendors", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Name_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Category_Input-")],    

    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Contact_First_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Contact_Last_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Contact_Preferred_Input-")],
    [sg.Multiline(f"", pad=((3,3),(3,10)), font=("",small_print), size=(view_vendors_data_width,2),justification="left", background_color=detailed_information_color, border_width=edit_account_border_width, disabled=True, key="-Vendor_Address_Input-")],
    #[sg.Text(f"",font=("",4), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],

    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(12,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Phone_Input-"), sg.OptionMenu(phone_types, pad=view_account_labels_pad+1, size=(8,1), background_color="white", disabled=True, key="-Vendor_PhoneType_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Email_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Website_Input-")],
    #[sg.Input(f"0.00", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Balance_Input-")],
]


view_vendor_labels_layout = [
    #[sg.Text(f"",font=("",2), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Text(f"Name: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Name_Display-")],    
    [sg.Text(f"Category: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Category_Display-")],    

    [sg.Text(f"First: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Contact_First_Display-")],
    [sg.Text(f"Last: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Contact_Last_Display-")],
    [sg.Text(f"Preferred: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Contact_Preferred_Display-")],
    [sg.Text(f"Address: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Address_Display-")],
    [sg.Text(f"",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Name_Display-")],    

    [sg.Text(f"Phone: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=((0, view_account_labels_pad),(0,6)),justification="left", background_color=detailed_information_color, key="-Vendor_Phone_Display-")],
    [sg.Text(f"Email: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Email_Display-")],
    [sg.Text(f"Website: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Website_Display-")],
    #[sg.Text(f"Balance: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad), justification="left", background_color=overview_information_color, key="-Vendor_Balance_Display-")],
]

view_vendor_frame_layout = [
    [sg.Input(f"Vendor Number", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Number_Display-")],    
    [sg.Column(layout=view_vendor_labels_layout, justification = "left", background_color=overview_information_color, size=(view_vendors_labels_width*6,view_vendors_data_height*9)), sg.Column(layout=view_vendors_edit_layout, justification = "left", background_color=overview_information_color, size=(view_vendors_data_width*6,view_vendors_data_height*9) )],
    [sg.Text(f"Memo: ", font=("",small_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Multiline(f"Notes:", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,4),justification="left", background_color=detailed_information_color, key="-Vendor_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Vendor", disabled=False,  key="-Edit_Vendor_Button-")],
]

view_vendors_tab_column_1 = [
    [sg.Frame("Vendor: ", layout=view_vendor_frame_layout, size=(275,600),font=("",medium_print,"bold"), key="-View_Vendor_Frame-", background_color=overview_information_color)],
]

view_vendors_tab_column_2 = [
    [sg.Table(values=[],row_height=36, col_widths=[8,32,20,22,20], cols_justification=["c","c","c","c","c"], auto_size_columns=False, headings=["Vendor", "Name", "Contact", "Phone", "Email"], num_rows=16, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-View_Vendors_Content-", background_color=detailed_information_color)],
]

vendors_tab = [
    #[sg.Text(font=("",medium_print), size=(133,1), justification="center")],
    [sg.Column(view_vendors_tab_column_1, size=(280,610), element_justification="left"), sg.Column(view_vendors_tab_column_2, size=(960,610), element_justification="center", expand_x=True, expand_y=False)],
    [sg.Push(),sg.Input("",(20,1),disabled=False, enable_events=True, key="-Vendors_Search_Input-"), sg.Button("New Vendor",enable_events=True, key="-New_Vendor_Button-"),sg.Text(" ")],
]

view_customers_data_height = 30
view_customers_labels_width = 10
view_customers_data_width = 30

view_customers_edit_layout = [
    [sg.Text(f"",font=("",2), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"No Customers", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Name_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Contact_First_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Contact_Last_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Contact_Preferred_Input-")],
    [sg.Multiline(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,2),justification="left", background_color=detailed_information_color, border_width=edit_account_border_width, disabled=True, key="-Customer_Address_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(12,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Phone_Input-"), sg.OptionMenu(phone_types, pad=view_account_labels_pad+1, size=(8,1), background_color="white", disabled=True, key="-Customer_PhoneType_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Email_Input-")],
]

view_customers_labels_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Text(f"Name: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Name_Display-")],    
    [sg.Text(f"First: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Contact_First_Display-")],
    [sg.Text(f"Last: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Contact_Last_Display-")],
    [sg.Text(f"Preferred: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Contact_Preferred_Display-")],
    [sg.Text(f"Address: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Address_Display-")],
    [sg.Text(f"", font=("",6), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color)],

    [sg.Text(f"Phone: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Phone_Display-")],
    [sg.Text(f"Email: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Email_Display-")],
]

view_customers_frame_layout = [
    [sg.Input(f"Customer Number", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Number_Display-")],    
    [sg.Column(layout=view_customers_labels_layout, justification = "left", background_color=overview_information_color, size=(view_customers_labels_width*6,view_customers_data_height*7)), sg.Column(layout=view_customers_edit_layout, justification = "left", background_color=overview_information_color, size=(view_customers_data_width*6,view_customers_data_height*8) )],
    [sg.Text(f"Memo: ", font=("",small_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Multiline(f"Notes:", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,4),justification="left", background_color=detailed_information_color, key="-Customer_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Customer", disabled=False,  key="-Edit_Customer_Button-")],
]

view_customers_tab_column_1 = [
    [sg.Frame("Customer: ", layout=view_customers_frame_layout, size=(275,600),font=("",medium_print,"bold"), key="-View_Customer_Frame-", background_color=overview_information_color)],
]

view_customers_tab_column_2 = [
    [sg.Table(values=[],row_height=36, col_widths=[10,24,20,14,20,14], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, headings=["Customer", "Name", "Contact", "Phone", "Email", "Balance"], num_rows=16, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-View_Customers_Content-", background_color=detailed_information_color)],
]

customers_tab = [
    #[sg.Text(font=("",medium_print), size=(133,1), justification="center")],
    [sg.Column(view_customers_tab_column_1, size=(280,610), element_justification="left"), sg.Column(view_customers_tab_column_2, size=(960,610), element_justification="center", expand_x=True, expand_y=False)],
    [sg.Push(),sg.Input("",(20,1),disabled=False, enable_events=True, key="-Customers_Search_Input-"), sg.Button("New Customer",enable_events=True, key="-New_Customer_Button-"),sg.Text(" ")],
]

view_services_edit_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Service_Sku_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Service_Description_Input-")],    

    #[sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Service_Photo_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Service_Price_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Service_Taxable_Input-")],
 ]

view_services_labels_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Text(f"SKU: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Service_Name_Display-")],    
    [sg.Text(f"Description: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Service_Category_Display-")],    

    [sg.Text(f"Photo: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Service_Contact_First_Display-")],
    [sg.Text(f"Price: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Service_Contact_Last_Display-")],
    [sg.Text(f"Taxable: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Service_Contact_Preferred_Display-")],
]

view_services_frame_layout = [
    [sg.Input(f"SKU", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Service_Number_Display-")],    
    [sg.Column(layout=view_services_labels_layout, justification = "left", background_color=overview_information_color, size=(view_customers_labels_width*6,view_customers_data_height*4)), sg.Column(layout=view_services_edit_layout, justification = "left", background_color=overview_information_color, size=(view_customers_data_width*6,view_customers_data_height*4) )],
    [sg.Text(f"Memo: ", font=("",small_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Multiline(f"Long Description:", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,4),justification="left", background_color="white", key="-Service_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit SKU", disabled=False,  key="-Edit_Service_Button-")],
]

view_services_tab_column_1 = [
    [sg.Frame("Service: ", layout=view_services_frame_layout, size=(275,600),font=("",medium_print,"bold"), key="-View_Service_Frame-", background_color=overview_information_color)],
]

view_services_tab_column_2 = [
    [sg.Table(values=[],row_height=36, col_widths=[12,48,20,20], cols_justification=["c","c","c","c"], auto_size_columns=False, headings=["SKU", "Description", "Price", "Taxable?"], num_rows=16, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-View_Services_Content-", background_color=detailed_information_color)],
]

services_tab = [
    [sg.Column(view_services_tab_column_1, size=(280,610), element_justification="left"), sg.Column(view_services_tab_column_2, size=(960,610), element_justification="center", expand_x=True, expand_y=False)],
    [sg.Push(),sg.Input("",(20,1),disabled=False, enable_events=True, key="-Services_Search_Input-"), sg.Button("New Service",enable_events=True, key="-New_Service_Button-"),sg.Text(" ")],
]

view_pos_edit_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_CustomerName_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_CustomerContact_Input-")], 
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_CustomerEmail_Input-")],

    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_CustomerPhone_Input-")],   
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_TrackingCode_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_Subtotal_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_SalesTax_Input-")],
    
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_Total_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_DueDate_Input-")],
    [sg.OptionMenu([f"Due","Overdue","Paid","Refunded","Canceled"], disabled=True, pad=view_account_labels_pad+1, size=(view_customers_data_width,1),background_color="white", key="-POS_Status_Input-")],
]

view_pos_labels_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],detailed_information_color
    [sg.Text(f"Customer: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-POS_Name_Display-")],    
    [sg.Text(f"Contact: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-POS_Contact_Display-")],    
 
    [sg.Text(f"Email: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-POS_Email_Display-")],    

    [sg.Text(f"Phone: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-POS_Phone_Display-")],
    [sg.Text(f"Code: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-POS_Code_Display-")],
    [sg.Text(f"Subtotal: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-POS_Subtotal_Display-")],
    [sg.Text(f"Sales Tax: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-POS_SalesTax_Display-")],

    [sg.Text(f"Total: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-POS_Total_Display-")],
    [sg.Text(f"Due Date: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-POS_Due_Date_Display-")],
    [sg.Text(f"Status: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-POS_Status_Display-")],

]

view_pos_frame_layout = [
    [sg.Input(f"Invoice Number", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-POS_Number_Display-")],    
    [sg.Column(layout=view_pos_labels_layout, justification = "left", background_color=overview_information_color, size=(view_customers_labels_width*6,view_customers_data_height*8)), sg.Column(layout=view_pos_edit_layout, justification = "left", background_color=overview_information_color, size=(view_customers_data_width*6,view_customers_data_height*8) )],
    [sg.Text(f"", font=("",small_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    #[sg.Multiline(f"Notes:", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,4),justification="left", background_color=detailed_information_color, key="-POS_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"View Invoice", disabled=False,  key="-View_POS_Button-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Invoice", disabled=False,  key="-Edit_POS_Button-")],
]

pos_tab_column_1 = [
    [sg.Frame("POS: ", layout=view_pos_frame_layout, size=(275,600),font=("",medium_print,"bold"), key="-View_POS_Frame-", background_color=overview_information_color)],
]

pos_tab_column_2 = [
    [sg.Table(values=[],row_height=36, col_widths=[12,20,16,22,16,16], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, headings=["Invoice","Customer Name", "Phone", "Email", "Total", "Status"], num_rows=16, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-View_POS_Content-", background_color=detailed_information_color)],
]

POS_tab = [
    [sg.Column(pos_tab_column_1, size=(280,610), element_justification="left"), sg.Column(pos_tab_column_2, size=(960,610), element_justification="center", expand_x=True, expand_y=False)],
    [sg.Push(),sg.Input("",(20,1),disabled=False, enable_events=True, key="-POS_Search_Input-"), sg.Button("New Invoice",enable_events=True, key="-New_Invoice_Button-"),sg.Text(" ")],
]

inventory_tab = [
    [sg.Text(font=("",medium_print), size=(133,1))],
    [sg.Text("Inventory")],

]

owner_equity_tab = [
    [sg.Text(font=("",medium_print), size=(133,1))],
    [sg.Text("Owners:", font=("",medium_print), size=(133,1))],
]

view_account_edit_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"10001", pad=view_account_labels_pad+1, font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Number_Input-")],    
    [sg.Input(f"Asset", pad=view_account_labels_pad+1,font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Type-")],
    [sg.Input(f"Greylock FCU", pad=view_account_labels_pad+1, font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Bank-")],
    [sg.Input(f"Checking", pad=view_account_labels_pad+1, font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Bank_Acct_Type-")],
    [sg.Input(f"1234567890", pad=view_account_labels_pad+1, font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Bank_Acct_Number-")],
    [sg.Input(f"0987654321", pad=view_account_labels_pad+1,font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Bank_Acct_Routing-")],
    [sg.Input(f"6543.21", pad=view_account_labels_pad+1, font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Debits-")],
    [sg.Input(f"1234.56", pad=view_account_labels_pad+1, font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Credits-")],
    [sg.Input(f"{6543.21-1234.56}", pad=view_account_labels_pad+1, font=("",small_print), size=(account_information_labels_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Balance-")],
]

view_account_labels_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Text(f"Account Number: ",font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Account_Number_Display-")],
    [sg.Text(f"Account Type: ",font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Account_Type_Display-")],
    [sg.Text(f"Bank or Credit Union: ", font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Account_Bank_Display-")],
    [sg.Text(f"Bank Account Type: ", font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Account_Bank_Acct_Type_Display-")],
    [sg.Text(f"Bank Account Number: ", font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Account_Bank_Acct_Number_Display-")],
    [sg.Text(f"Bank Routing Number: ",font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad), justification="left", background_color=overview_information_color, key="-Account_Bank_Acct_Routing_Display-")],
    [sg.Text(f"Total Debits: ", font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Account_Debits_Display-")],
    [sg.Text(f"Total Credits: ", font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Account_Credits_Display-")],
    [sg.Text(f"Balance: ", font=("",small_print), size=(account_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Account_Balance_Display-")],
]

view_account_column_height = len(view_account_labels_layout)*24

view_account_frame_layout = [
    [sg.Input(f"Joint Bank Account", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Edit_Account_Name_Input-")],    
    [sg.Column(layout=view_account_labels_layout, justification = "left", background_color=overview_information_color, size=(account_information_labels_width*7,view_account_column_height)), sg.Column(layout=view_account_edit_layout, justification = "left", background_color=overview_information_color, size=(account_information_labels_width*5,view_account_column_height) )],
    [sg.Text(f"Notes: ", font=("",small_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Multiline(f"Notes and notes and notes and notes and lorum ipsum lebold valco hebonable ens je patetin", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,5),justification="left", background_color=detailed_information_color, key="-Account_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Account", disabled=True,  key="-Edit_Account_Button-")],
]



view_account_tab_column_1 = [
    [sg.Frame("Account: ", layout=view_account_frame_layout, size=(275,455),font=("",medium_print,"bold"), key="-View_Account_Frame-", background_color=overview_information_color)],
]
view_account_tab_column_2 = [
    [sg.Table(values=[],row_height=36, col_widths=[10,10,40,14,14,14], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, headings=["Transaction", "Date", "Name", "Credits", "Debits", "Balance"], num_rows=12, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-Account_Register_Content-", background_color=detailed_information_color)],
]


view_account_tab = [
    #[sg.Text(font=("",medium_print), size=(133,1), justification="center")],
    [sg.Column(view_account_tab_column_1, size=(280,460), element_justification="left"), sg.Column(view_account_tab_column_2, size=(960,460), element_justification="center", expand_x=True, expand_y=False)],
]

current_time_info = get_current_time_info()

application_messages_layout = [
    [sg.Text(icb_session.current_console_messages[0], size=(120,5), background_color=overview_information_color, key="-Console_Log-", font=("",medium_print), expand_x=True, expand_y=True)],
    ]

console_frame_layout = [
    [sg.Frame("Console", size=(1228,200), expand_x=True, expand_y=False, layout=application_messages_layout, background_color=overview_information_color, pad=4, element_justification="center", key='-Console_Frame_Layout-')] 
]

view_properties_tab = [
    [sg.Text("Business Name:", font=("",medium_print)), sg.Push(), sg.Input(size=(30,1), key=f"-edit_db_name-", font=("", medium_print))],
    [sg.Text("Address"), sg.Push(), sg.Multiline("",size=(22,2),key=f"-Edit_Business_Address-",)],
    [sg.Text("Owner or Financial Officer Name:"), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Officer-",)],
    [sg.Text("Title or Position:"), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Officer_Title-",)],
    [sg.Text("Phone Number: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Phone-",)],
    [sg.Text("Email: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Email-",)],
    [sg.Text("EIN or SSN: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_EIN-",)],
    [sg.Text("Receipts Repository: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Receipts_Repository-",)],
    [sg.Text("Sales Tax %: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Sales_Tax-",)],
    [sg.Multiline("Notes: ", size=(62,9),key=f"-Edit_Business_Notes-",)],
    [sg.Push(),sg.Button("Save Properties", size=(16,1), font=("", medium_print), enable_events=True, key="-Save_Revised_Properties-")],
]

transaction_information_labels_width = 10

transaction_information_width = 43- transaction_information_labels_width

view_ledger_labels_layout = [
    [sg.Text(f"Name: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Name_Display-")],
    [sg.Text(f"Date: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Date_Display-")],
    [sg.Text(f"Recorded: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Recorded_Display-")],
    [sg.Text(f"Edited: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Edited_Display-")],
    [sg.Text(f"Amount: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Amount_Display-")],
    [sg.Text(f"Credit Acct: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Credit_Display-")],
    [sg.Text(f"Debit Acct: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Debit_Display-")],
    [sg.Text(f"Customer: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Customer_Display-")],
    [sg.Text(f"Vendor: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Vendor_Display-")],
]

view_ledger_edit_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Name_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Date_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Recorded_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Edited_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Amount_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Credit_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Debit_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Customer_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(transaction_information_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Ledger_Vendor_Input-")],

]

#default_logo = Image.open("50666888.jpg")
#default_logo.save("50666888.png")
view_transaction_column_height = 212

view_ledger_frame_layout = [
    [sg.Input(f"Transaction Number", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Transaction_Number_Display-")],    
    [sg.Column(layout=view_ledger_labels_layout, justification = "left", background_color=overview_information_color, size=(transaction_information_labels_width*7,view_transaction_column_height)), sg.Column(layout=view_ledger_edit_layout, justification = "left", background_color=overview_information_color, size=(transaction_information_width*8,int(view_transaction_column_height)) )],
    [sg.Multiline(f"", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,3),justification="left", background_color=detailed_information_color, key="-Transaction_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button("Record", key="-Transaction_Image_Button-", enable_events=True)],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Transaction", disabled=False,  key="-Edit_Transaction_Button-")],
]


view_ledger_tab_column_1 = [
    [sg.Frame("Transaction: ", layout=view_ledger_frame_layout, size=(298,700),font=("",medium_print,"bold"), key="-View_Ledger_Frame-", background_color=overview_information_color)],
]
view_ledger_tab_column_2 = [
    [sg.Text(f"Ledger: None", expand_x=True, font=("",medium_print), justification="center", key="-Ledger_Title_Display-")],
    [sg.Table(values=[],row_height=36, col_widths=[7,50,12,10,10,10], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, header_font=("",small_print),headings=["Transaction", "Name", "Amount", "Debit Account", "Credit Account", "Date"], num_rows=18, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, key="-Ledger_Display_Content-", background_color=detailed_information_color)],
    [sg.Push(),sg.Combo(values=["All Years"], default_value="All Years", enable_events=True, key="-Ledger_Year_Picker-"), sg.Input("",(20,1),disabled=False, enable_events=True, key="-Ledger_Search_Input-"),sg.Button("New Transaction",enable_events=True, key="-New_Transaction_Button-"),sg.Text(" ")],

]

ledger_tab = [
    [sg.Column(view_ledger_tab_column_1, size=(300,755), element_justification="left"), sg.Column(view_ledger_tab_column_2, size=(935,755), element_justification="center", expand_x=True, expand_y=False)],
]

about_tab = [
    [sg.Text(f"\n\nAbout Iceberg: \nVersion 1.1\n\nDeveloped in the United States by Joseph M. Basile \n\nMIT License 2024", expand_x=True, font=("",medium_print), justification="center")],
]

#-------------Overall Layout------------------------

current_time = get_current_time_info()
#current_year

layout1 = [
    [sg.Menu(menu_def, key="-Program_Menu-")],
    [sg.Text(f"""No Data Loaded""", key="-Load_Messages-", font=("",large_print), size=(20,1), justification="center", expand_x=True)],
#    [sg.Column([[sg.Text("Year: ", font=("",medium_print)),sg.OptionMenu(values=[f"CY{current_year}"], auto_size_text=True, default_value=f"CY{current_year}",key="-Year_Picker-")]], justification="center", element_justification="center")],
    [sg.Text(current_time[0], key='-Current_Time_Display-', font=("",medium_print), size=(133,1), justification="center", visible=True, expand_x=True)],
    [sg.TabGroup([
        [sg.Tab('Dashboard', layout=dashboard_tab, key='-Dashboard_Tab-')],#0
        [sg.Tab('View Ledger', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=ledger_tab, size=(800,800))]], visible=False, pad=2, key='-Ledger_Tab-')],#1
        [sg.Tab('Reports', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=reports_tab, size=(800,800))]], visible=False, pad=2, key='-Reports_Tab-')],#2
        [sg.Tab('Vendors', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=vendors_tab, size=(800,800))]], visible=False, pad=2, key='-Vendors_Tab-')],#3
        [sg.Tab('Customers', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=customers_tab, size=(800,800))]], visible=False, pad=2, key='-Customers_Tab-')],#4
        [sg.Tab('Point of Sale', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=POS_tab, size=(800,800))]], visible=False, pad=2, key='-Invoicing_Tab-')],#5
        [sg.Tab('Inventory', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=inventory_tab, size=(800,800))]], visible=False, pad=2, key='-Inventory_Tab-')],#6
        [sg.Tab('Owner Equity', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=owner_equity_tab, size=(800,800))]], visible=False, pad=2, key='-Owner_Equity_Tab-')],#7
        [sg.Tab('View Account', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=view_account_tab, size=(800,800))]], visible=False, pad=2, key='-View_Account_Tab-')],#8
        [sg.Tab('Database Properties', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=view_properties_tab, size=(800,800))]], visible=False, pad=2, key='-View_Properties_Tab-')],#9   
        [sg.Tab('Services', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=services_tab, size=(800,800))]], visible=False, pad=2, key='-View_Services_Tab-')],#10   
        [sg.Tab('About', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=about_tab, size=(800,800))]], visible=False, pad=2, key='-About_Tab-')],#11  
    ], expand_x=True, expand_y=True, key='-Display_Area-', size=(800,720))   ],
    [sg.Column(console_frame_layout, size=(900,60), expand_x=True, key="-Console_Column-", scrollable=True, vertical_scroll_only=True)], #scrollable=False,
]


tab_keys = ['-Dashboard_Tab-','-Ledger_Tab-','-Reports_Tab-','-Vendors_Tab-','-Customers_Tab-','-Invoicing_Tab-','-Inventory_Tab-','-Owner_Equity_Tab-','-View_Account_Tab-','-View_Properties_Tab-','-View_Services_Tab-', "-About_Tab-"]


#░▒▓███████▓▒░   ░▒▓██████▓▒░  ░▒▓███████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░   ░▒▓███████▓▒░ 
#░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        
#░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        
#░▒▓███████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░   ░▒▓██████▓▒░  
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░               ░▒▓█▓▒░ 
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░               ░▒▓█▓▒░ 
#░▒▓█▓▒░         ░▒▓██████▓▒░  ░▒▓█▓▒░         ░▒▓██████▓▒░  ░▒▓█▓▒░        ░▒▓███████▓▒░ 



def new_database_layout(num):
    num = num + 1
    new_database_layout = [
        [sg.Text("Business Name*:", font=("",medium_print)), sg.In(size=(30,1), key=f"-db_name_{num}-", font=("", medium_print)), sg.Text(".icb", font=("", medium_print))],
        [sg.Push(), sg.Text("Filekey Save Location*: ", font=("", medium_print)),sg.FolderBrowse(size=(16,1), enable_events=True, key=f"-Save_Location_{num}-", font=("", medium_print))],
        [sg.Text("Address*:"), sg.Push(), sg.Multiline("",size=(23,2),key=f"-Business_Address_{num}-",)],
        [sg.Text("Owner or Financial Officer Name:"), sg.Push(), sg.In("",(25,1),key=f"-Business_Officer_{num}-",)],
        [sg.Text("Title or Position:"), sg.Push(), sg.In("",(25,1),key=f"-Business_Officer_Title_{num}-",)],
        [sg.Text("Phone Number:"), sg.Push(), sg.In("",(25,1),key=f"-Business_Phone_{num}-",)],
        [sg.Text("Email:"), sg.Push(), sg.In("",(25,1),key=f"-Business_Email_{num}-",)],
        [sg.Text("EIN or SSN:"), sg.Push(), sg.In("",(25,1),key=f"-Business_EIN_{num}-",)],
        [sg.Text("Sales Tax %*:"), sg.Push(), sg.In("0.00",(25,1),key=f"-Business_SalesTax_{num}-",)],
        [sg.Push(), sg.Text("Receipts Respository Location*: ", key=f"-Business_Receipts_Repository_Label_{num}-"), sg.FolderBrowse("Receipts Folder",font=("",small_print),key=f"-Business_Receipts_Repository_{num}-", enable_events=True)],
        [sg.Multiline("Notes: ", size=(62,9),key=f"-Business_Notes_{num}-",)],
        [sg.Column([[sg.Button(button_text="Submit",size=(20,1),key=f'-Submit_New_Database_Button_{num}-', enable_events=True)],[sg.Sizer(460,60)]],justification="center", size=(480,60),element_justification="center",expand_x=True)],
    ]
    
    return new_database_layout, num


def open_database_layout(num):
    num = num + 1
    open_database_layout = [
        [sg.Text("Filekey Save Location: ", font=("", medium_print)),sg.FileBrowse(size=(20,1), enable_events=True, key=f"-Open_File_{num}-", font=("", medium_print), file_types=[("Iceberg Keys","*.icbkey")])],
        [sg.Button("Open",key=f'-Open_Database_Button_{num}-', enable_events=True)],
    ]
    
    return open_database_layout, num

def new_transaction_layout(num):
    num = num + 1
    count_transactions_query = f"""SELECT MAX(Transaction_ID) AS [Number_of_Records] FROM {icb_session.ledger_name};"""
    transaction_number = db.execute_read_query_dict(icb_session.connection, count_transactions_query)
    transaction_number_str = "1"
    #print(count_transactions_query)
    #print("transaction_number")
    #print(transaction_number)
    if type(transaction_number) != str:
        num_records = transaction_number[0]['Number_of_Records']
        if num_records == None or num_records == "None":
            num_records = 0
        transaction_number_str = f"""{int(num_records)+1}"""
    account_repo = AccountRepository(icb_session.connection)
    icb_session.all_accounts = account_repo.get_all()
    these_accounts = []
    for account in icb_session.all_accounts:
        these_accounts.append(f"""{account['Account_ID']} - {account['Name']}""") 
    vendor_repo = VendorRepository(icb_session.connection)
    icb_session.vendors = vendor_repo.get_all()
    these_vendors = [""]
    if len(icb_session.vendors)>0:
        for vendor in icb_session.vendors:
            these_vendors.append(f"""{vendor['Vendor_ID']} - {vendor['Business_Name']}""") 
            #print("vendors")
            #print(icb_session.vendors)
    else:
        these_vendors.append("None")


    new_transaction_column_1 = [
        [sg.Image("checkbook_art_free.png",size=(50,50),subsample=1),sg.Text(f"Transaction {transaction_number_str}", size=(13,1), font=("Bold",large_print),justification="center", pad=(0,0), key=f"-Transaction_Title_{num}-")],
        [sg.Text("Transaction Name*: ", font=("",medium_print)), sg.Push(), sg.Input(size=(20,1), key=f"-Transaction_Name_{num}-", font=("", medium_print) )],
        [sg.Text("Transaction Date*: ", font=("",medium_print)), sg.Push(),sg.Input("",size=(12,1),font=("",medium_print), key=f"-Transaction_Date_String_{num}-"), sg.CalendarButton(f"Select Date",format= "%Y-%m-%d", size=(16,1),key=f"-Transaction_Date_{num}-", enable_events=True)],
        [sg.Text("Amount*: ", font=("",medium_print)), sg.Push(), sg.Text("$",size=(1,1),font=("",medium_print)), sg.Input("",(16,1),key=f"-Transaction_Amount_{num}-")],
        [sg.Text("Debit Account*: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(these_accounts,key=f"-Transaction_Debit_Account_{num}-")],
        [sg.Text("Credit Account*: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(these_accounts,key=f"-Transaction_Credit_Account_{num}-")],
        [sg.Text("Vendor: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(these_vendors,key=f"-Transaction_Vendor_{num}-")],
        #[sg.Text("Customer: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(["","Pauli Portabello","Sally Swiss Chard","Officer Acorn Squash"],key=f"-Transaction_Customer_{num}-")],
        [sg.Push(), sg.Multiline("Notes: ", font=("",medium_print), size=(44,4),key=f"-Transaction_Notes_{num}-")],
    ]
    
    new_transaction_column_2 = [
        [sg.Column(layout=[[sg.Image(logo,size=(350,360), enable_events=False, key=f"-Transaction_Image_Display_{num}-", subsample=3)],[sg.FileBrowse("Select Image",enable_events=True, key=f"-Transaction_Image_Input_{num}-")]],size=(350,400),element_justification="center",justification="center")],
    ]

    new_transaction_layout = [
        [sg.Column(layout=new_transaction_column_1,pad=0),sg.Column(new_transaction_column_2,pad=0)],
        [sg.Column([[sg.Button(button_text="Submit",size=(20,1),key=f'-Submit_Transaction_Button_{num}-', enable_events=True)],[sg.Sizer(780,0)]],justification="center", size=(780,60),element_justification="center",expand_x=True)],
    ]
    
    return new_transaction_layout, num


def new_account_layout(num):
    """Layout for a new account window."""

    num = num + 1
    icb_session.num = num

    new_account_column = [
        [sg.Image("checkbook_art_free.png",size=(50,50),subsample=1),sg.Text(f"New Account", size=(13,1), font=("Bold",large_print),justification="center", key=f"-Account_Title_{num}-")],
        [sg.Text("Account Name*: ", font=("",medium_print)), sg.Push(), sg.Input(size=(20,1), key=f"-Account_Name_{num}-", font=("", medium_print) )],
        [sg.Text("Account Type*: ", font=("",medium_print)), sg.Push(), sg.Push(), sg.OptionMenu(values=["10 Assets","11 Expenses", "12 Withdrawals", "13 Liabilities", "14 Owner Equity", "15 Revenue"], auto_size_text=True, default_value="10 Assets",key=f"-Account_Type_Picker_{num}-")],
        [sg.Text("Bank: ", font=("",medium_print)), sg.Push(), sg.Input("",(16,1),key=f"-Account_Bank_{num}-")],
        [sg.Text("Bank Account Type: ", font=("",medium_print)), sg.Push(), sg.Input("",key=f"-Account_Bank_Account_Type_{num}-", size=(16,1), enable_events=False)],
        [sg.Text("Bank Account Number: ", font=("",medium_print)), sg.Push(), sg.Input("",key=f"-Account_Bank_Account_Number_{num}-", size=(16,1), enable_events=False)],
        [sg.Text("Bank Routing: ", font=("",medium_print)), sg.Push(), sg.Input("",key=f"-Account_Bank_Routing_{num}-")],
        [sg.Multiline("Notes: ", font=("",medium_print), size=(44,8),key=f"-Account_Notes_{num}-")],
    ]
    
    new_account_layout = [
        [sg.Column(layout=new_account_column,pad=0)],
        [sg.Column([[sg.Button(button_text="Submit",size=(20,1),key=f'-Submit_Account_Button_{num}-', enable_events=True)],[sg.Sizer(480,0)]],justification="center", size=(480,60),element_justification="center",expand_x=True)],
    ]
    
    return new_account_layout, num


def new_invoice_layout(num):
    num = num + 1
    account_repo = AccountRepository(icb_session.connection)
    these_asset_accounts = account_repo.get_by_type_prefix('10')
    #print(these_asset_accounts)
    asset_accounts = []
    if these_asset_accounts != []:
        for account in these_asset_accounts:
            asset_accounts.append(f"{account['Account_ID']} {account['Name']}")


    new_invoice_column_1 = [
        [sg.Input('',key=f"-Invoice_Customer_Search_{num}-",enable_events=True)],
        [sg.Table([],headings=["ID","Company Name", "First Name", "Last Name"],col_widths=(5,16, 16, 16), num_rows=5,enable_events=True, key = f'-Invoice_Customers_Results_{num}-')],
        [sg.Text("Customer Name: ", font=("",medium_print)), sg.Push(),  sg.Input("", disabled=True, key=f"-Invoice_Customer_Name_{num}-", enable_events=False, size=(20,1))],
        [sg.Text("Customer Address*: ", font=("",medium_print)), sg.Push(), sg.Multiline(size=(18,2), disabled=True, key=f"-Invoice_Customer_Address_{num}-", font=("", medium_print) )],
        [sg.Text("Customer Contact: ", font=("",medium_print)), sg.Push(), sg.Input("", disabled=True,size=(20,1),font=("",medium_print), key=f"-Invoice_Customer_Contact_{num}-")],
        [sg.Text("Status*: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(["Due", "Overdue", "Paid"],"Due",key=f"-Invoice_Status_{num}-")],
        [sg.Text("Due Date*: ", font=("",medium_print)), sg.Push(), sg.Input("",size=(10,1),key=f"-Invoice_Due_Date_{num}-", enable_events=False),sg.CalendarButton("Select Date", format= "%Y-%m-%d", location=(500,500),key=f"-Invoice_Due_Date_Selector_{num}-")],
        [sg.OptionMenu(asset_accounts,asset_accounts[5],key=f"-Invoice_Debit_{num}-")],
    ] 
    
    new_invoice_column_2 = [
        [sg.Input("", key=f"-Invoice_Search_Input_{num}-", enable_events=True)],
        [sg.Table([],headings=["Sku  ","Description  ", "Price  ", "Taxable"],col_widths=(16,30, 20, 10), num_rows=5,enable_events=True,key=f'-Invoice_Search_Content_{num}-')],
        [sg.Button('Remove Line Item', key=f"-Invoice_Remove_Button_{num}-"), sg.Text("Qty: "), sg.Input(size=(3,1), key=f"-Invoice_Quantity_Input_{num}-"), sg.Button("Add Line Item", key=f"-Invoice_Add_Button_{num}-")],
        [sg.Table([],headings=["Sku","Description", "Price  ", "Qty ","Total    "],num_rows=5,key=f"-Invoice_Line_Items_{num}-")],
        [sg.Text("Subtotal*"), sg.Push(), sg.Text("$"), sg.Input(size=(10,1), disabled=True, key=f"-Invoice_Subtotal_{num}-")],
        [sg.Text("Sales Tax"), sg.Input(f"{dec(icb_session.sales_tax)*100}", size=(10,1), key=f"-Invoice_SalesTax_Rate_{num}-"),sg.Push(), sg.Text("$"), sg.Input(size=(10,1), disabled=True, key=f"-Invoice_SalesTax_{num}-")],
        [sg.Text("Total*"), sg.Push(), sg.Text("$"), sg.Input(size=(10,1), disabled=True, key=f"-Invoice_Total_{num}-")],
    ]




    new_invoice_layout = [
        [sg.Column(layout=new_invoice_column_1,pad=0, size= (380,340)),sg.Column(new_invoice_column_2,pad=0, size=(500, 340))],
        [sg.Column([[sg.Push(),sg.Button(button_text="Submit",size=(20,1),key=f'-Submit_Invoice_Button_{num}-', enable_events=True), sg.Push()]],justification="center", size=(780,60),element_justification="center",expand_x=True)],
    ]
    
    


    return new_invoice_layout, num

def invoice_paid_layout(num):
    num = num + 1
    account_repo = AccountRepository(icb_session.connection)
    asset_accounts = account_repo.get_by_type_prefix('10')
    #print(asset_accounts)
    accounts = []
    for account in asset_accounts:
        accounts.append(f"{account['Account_ID']} {account['Name']}")
    invoice_paid_layout = [
        [sg.OptionMenu(accounts,size=(36,1), key=f"-Invoice_Debit_Acct_{num}-")],
        [sg.Button("Save",key=f'-Invoice_Transactions_Button_{num}-', enable_events=True)],
    ]

    final_layout = [
        [sg.Column(invoice_paid_layout,size=(300,200),element_justification='center')],
    ]
    
    return final_layout, num

def remove_account_in_use(window, values, event):
    """Removes an account from icb_session.all_accounts 
    to prevent transactions with debits and credits to 
    the same account. Returns the all_accounts list with 
    the in-use account removed."""
    num = icb_session.num
    #print("removing account")
    #print(values[event])
    account_number = int(values[event][0:5])
    #print(account_number)
    revised_accounts = []
    for account in icb_session.all_accounts:
        #print(account)
        if account['Account_ID'] != account_number:
            revised_accounts.append(account)
        else:
            print(f"Removing: {account['Account_ID']}")
    return revised_accounts

def new_vendor_layout(num,vendor_number):
    num = num + 1
    new_vendor_layout = [
        [sg.Text(f"Vendor Number: {vendor_number}", font=("",medium_print),expand_x=True, justification="center")],
        [sg.Text("Business Name*: ", font=("",medium_print)), sg.Push(), sg.Input("",(30,1),key=f"-Vendor_Name_{num}-",)],
        [sg.Text("Merchant Category: ", font=("",medium_print)), sg.Push(), sg.Input("",(30,1),key=f"-Vendor_Category_{num}-",)],
        [sg.Text("Contact First Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Contact_First_{num}-", size=(30,1))],
        [sg.Text("Contact Last Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Contact_Last_{num}-", size=(30,1))],
        [sg.Text("Contact Preferred Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Contact_Preferred_{num}-", size=(30,1))],
        [sg.Text("Phone:", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Phone_{num}-", size=(17,1)), sg.OptionMenu(phone_types,"Mobile",key=f"-Vendor_Phone_Type_{num}-")],
        [sg.Text("Address: ", font=("",medium_print)), sg.Push(), sg.Multiline(key=f"-Vendor_Address_{num}-", size=(28,2))],
        [sg.Text("Email: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Email_{num}-", size=(30,1))],
        [sg.Text("Website: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Website_{num}-", size=(30,1))],
        [sg.Multiline("Notes: ", font=("",medium_print), size=(62,4),key=f"-Vendor_Notes_{num}-",)],
        [sg.Column([[sg.Button(button_text="Add Vendor",size=(20,1),key=f'-Submit_Vendor_Button_{num}-', enable_events=True)],[sg.Sizer(460,60)]],justification="center", size=(480,60),element_justification="center",expand_x=True)],

    ]
    
    return new_vendor_layout, num    


def new_customer_layout(num,customer_number):
    num = num + 1
    new_customer_layout = [
        [sg.Text(f"Customer Number: {customer_number}", font=("",medium_print),expand_x=True, justification="center")],
        [sg.Text("Business Name: ", font=("",medium_print)), sg.Push(), sg.Input("",(30,1),key=f"-Customer_Name_{num}-",)],
        [sg.Text("Contact First Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Customer_Contact_First_{num}-", size=(30,1))],
        [sg.Text("Contact Last Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Customer_Contact_Last_{num}-", size=(30,1))],
        [sg.Text("Contact Preferred Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Customer_Contact_Preferred_{num}-", size=(30,1))],
        [sg.Text("Phone:", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Customer_Phone_{num}-", size=(17,1)), sg.OptionMenu(phone_types,"Mobile",key=f"-Customer_Phone_Type_{num}-")],
        [sg.Text("Address*: ", font=("",medium_print)), sg.Push(), sg.Multiline(key=f"-Customer_Address_{num}-", size=(28,2))],
        [sg.Text("Email: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Customer_Email_{num}-", size=(30,1))],
        [sg.Multiline("Notes: ", font=("",medium_print), size=(62,4),key=f"-Customer_Notes_{num}-",)],
        [sg.Column([[sg.Button(button_text="Add Customer",size=(20,1),key=f'-Submit_Customer_Button_{num}-', enable_events=True)],[sg.Sizer(460,60)]],justification="center", size=(480,60),element_justification="center",expand_x=True)],

    ]
    
    return new_customer_layout, num    

def new_service_layout(num,service_number):
    num = num + 1
    new_service_layout = [
        [sg.Text(f"Service Number: {service_number}", font=("",medium_print),expand_x=True, justification="center")],
        [sg.Text("Description*: ", font=("",medium_print)), sg.Push(), sg.Input("",(30,1),key=f"-Service_Description_{num}-",)],
        [sg.Text("Price*: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Service_Price_{num}-", size=(30,1))],
        [sg.Text("Taxable*: ", font=("",medium_print)), sg.Push(), sg.Combo(("True","False"),"False", key=f"-Service_Taxable_{num}-", size=(30,1))],
        [sg.Multiline("", font=("",medium_print), size=(62,4),key=f"-Service_Long_Description_{num}-",)],
        [sg.Column([[sg.Button(button_text="Add Service",size=(20,1),key=f'-Submit_Service_Button_{num}-', enable_events=True)],[sg.Sizer(460,60)]],justification="center", size=(480,60),element_justification="center",expand_x=True)],

    ]
    
    return new_service_layout, num    






#------------------------------------------Section 4 Data Functions

#░▒▓████████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░   ░▒▓██████▓▒░  ░▒▓████████▓▒░ ░▒▓█▓▒░  ░▒▓██████▓▒░  ░▒▓███████▓▒░   ░▒▓███████▓▒░ 
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░           ░▒▓█▓▒░     ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        
#░▒▓██████▓▒░   ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░           ░▒▓█▓▒░     ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░  
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░           ░▒▓█▓▒░     ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░        ░▒▓█▓▒░ 
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     ░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░        ░▒▓█▓▒░ 
#░▒▓█▓▒░         ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░     ░▒▓█▓▒░     ░▒▓█▓▒░  ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░ 

#Comment out the encryption functions that were moved to db_calls
#Remove when fully depreciated.




def synchronize_time(window, current_time_display):
    f"""Updates the time the first time after the program is opened. Returns Yes or No on whether the time updates are sychronized with the system time."""
    current_time = get_current_time_info()
    #print(values)
    if current_time_display[0] == current_time[0]:
        #print("Not Synchronized")
        return "No", current_time
    else:
        #print((current_time_display[0]))
        #print((current_time[0]))
        return "Yes", current_time


def update_time(window):
    f"""Updates the time at the top of the program."""
    current_time = get_current_time_info()
    window['-Current_Time_Display-'].update(current_time[0])
    return current_time

def create_database(values, current_console_messages,window, num, current_year):
    """Adds a new accounting database with the name given by the registering user."""

    

    #Create database
    db_name_1 = values[f"-db_name_{num}-"]
    db_name_2 = ""
    for chara in range(len(db_name_1)):
        if db_name_1[chara] == " " or db_name_1[chara] == "." or db_name_1[chara] == "," or db_name_1[chara] == "/" or db_name_1[chara] == "-" or db_name_1[chara] == r"'":
            db_name_2 = db_name_2 + "_"
        else:
            db_name_2 = db_name_2 + db_name_1[chara]
    icb_session.db_name = db_name_2 + f""".icb"""
    path_exists = os.path.exists(f"./{icb_session.db_name}")
    if path_exists==True:
        icb_session.console_log("DATABASE ALREADY EXISTS",icb_session.current_console_messages)
        return False, False, False
    #print(icb_session.db_name)
    if icb_session.connection == False:
        icb_session.connection = db.create_connection(f"./{icb_session.db_name}")
        #print(f"460 connection: {icb_session.connection}; {icb_session.db_name}")
    year = datetime.datetime.now().year


   #7 Create the Console_Log Table
    create_table_6_query = f"""CREATE TABLE tbl_Console_Log (Log_ID INTEGER NOT NULL"""
    
    lines = [   """, Console_Messages VARCHAR(9999) NOT NULL""", 
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, PRIMARY KEY ("Log_ID" AUTOINCREMENT)"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_6_query = create_table_6_query + lines[p]
    create_table_6_query = create_table_6_query + """);"""


    created_table = db.create_tables(icb_session.connection,create_table_6_query)
    print(f"{created_table}: tbl_Console_Log")


    #1 Create the Ledger

    ledger_name_1 = f"""ledger_{icb_session.db_name[:-4]}"""
    icb_session.ledger_name = f"""tbl_{ledger_name_1}_CY{year}"""


    create_table_1_query = f"""CREATE TABLE {icb_session.ledger_name} (Transaction_ID INTEGER NOT NULL"""
    lines = [""", Credit_Acct CHAR(5) NOT NULL""",
                """, Debit_Acct CHAR(5) NOT NULL""",
                """, Amount INTEGER NOT NULL""",
                """, Name VARCHAR(9999) NOT NULL""",
                """, Notes VARCHAR(9999)""",
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, Transaction_Date DATE NOT NULL""" ,
                """, Record_Image VARCHAR(9999) NOT NULL""" ,
                """, Vendor VARCHAR(9999)""",
                """, Customer VARCHAR(9999)""",
                """, PRIMARY KEY ("Transaction_ID" AUTOINCREMENT)""",
                """, CONSTRAINT chk CHECK (Amount>0)"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_1_query = create_table_1_query + lines[p]
    create_table_1_query = create_table_1_query + """);"""

    created_table = db.create_tables(icb_session.connection,create_table_1_query)
    #print(f"creating ledger: {create_table_1_query}")
    print(created_table)

    #2 Create the table of accounts and populate it with default accounts

    account_repo = AccountRepository(icb_session.connection)
    created_table = account_repo.create_table()
    print(created_table)

    #TODO:ADD IN DEFAULT ACCOUNTS


    default_accounts = [
        [10001,"Fixed Asset Real Estate","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10002,"Fixed Asset Bank Account Checking","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10003,"Misc Property","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10004,"Cash","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10005,"Product Inventory","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10006,"Accounts Receivable","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11001,"Office Supplies and Postage","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11002,"Advertising","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11003,"Commissions and Fees","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11004,"Contract Labor","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11005,"Asset Depreciations","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11006,"Insurance","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11007,"Mortgage Interest","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11008,"Legal and Professional Services","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11009,"Rent or Lease of Personal Property","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11010,"Rent or Lease of Real Property","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11011,"Repairs and Maintenance","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11012,"Supplies Expense - Non-Inventory","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11013,"Taxes and Licenses","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11014,"Business Travel Expenses","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11015,"Business Deductible Meals","Notes:  SEE IRS INSTRUCTIONS",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11016,"Utilties","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11017,"Other Expenses","Notes: SEE IRS INSTRUCTIONS",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [11018,"Cost of Goods Sold","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [12001,"Owner Equity Withdrawals","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [12002,"Owner Equity: Unclaimable Expenses","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [12003,"Owner Equity: Ask Accountant","Notes: Accountant or tax professional to review for claimable expenses.",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [13001,"Liabilities","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [13002,"Accounts Payable","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [13003,"Sales Tax Payable","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [14001,"Owner Equity Deposits","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [15001,"Sales","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [15002,"Real Estate Equity","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [15003,"Other Revenue","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
    ]

    for account in default_accounts:
        created_account = account_repo.insert(
            account[0],
            account[1],
            account[2],
            account[3],
            account[4],
            account[5],
            account[6],
            account[7],
            account[8]
        )
        current_console_messages = icb_session.console_log(message=created_account,current_console_messages=current_console_messages)
        print(created_account)


    #3 Create the Owners table

    owner_repo = OwnerRepository(icb_session.connection)
    created_table = owner_repo.create_table()


    #TODO: Collect user information during setup

    #4 Create the Vendors Table
    #4 Create the Vendors Table
    vendor_repo = VendorRepository(icb_session.connection)
    created_table = vendor_repo.create_table()
    icb_session.vendor_number = int(0)
    print(created_table)

    #5 Create the Customers Table
    customer_repo = CustomerRepository(icb_session.connection)
    created_table = customer_repo.create_table()
    print(created_table)

    #6 Create the Invoices Table
    invoice_repo = InvoiceRepository(icb_session.connection)
    created_table = invoice_repo.create_table()
    #print("Invoices_Table")
    print(created_table)



    #8 Create the Properties Table
    property_repo = PropertyRepository(icb_session.connection)
    created_table = property_repo.create_table()
    print(created_table)

    #Create the properties
    current_year
    icb_session.business_name = values[f'-db_name_{num}-']
    icb_session.business_address = values[f'-Business_Address_{num}-']
    icb_session.owner_name = values[f'-Business_Officer_{num}-']
    icb_session.owner_title = values[f'-Business_Officer_Title_{num}-']
    icb_session.owner_phone = values[f'-Business_Phone_{num}-']
    icb_session.owner_email = values[f'-Business_Email_{num}-']
    icb_session.owner_notes = values[f'-Business_Notes_{num}-']
    icb_session.business_ein = values[f'-Business_EIN_{num}-']
    icb_session.sales_tax = dec(values[f'-Business_SalesTax_{num}-'])/100
    
    icb_session.receipts_location = values[f'-Business_Receipts_Repository_{num}-']

    property_repo.insert("Business Name", icb_session.business_name, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Address", icb_session.business_address, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Owner or Financial Officer Name", icb_session.owner_name, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Title or Position", icb_session.owner_title, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Phone Number", icb_session.owner_phone, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Email", icb_session.owner_email, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Notes", icb_session.owner_notes, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("EIN or SSN", icb_session.business_ein, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Receipts Repository Location", icb_session.receipts_location, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Ledger Name", icb_session.ledger_name, "", icb_session.current_time_display[0], icb_session.current_time_display[0])
    property_repo.insert("Sales Tax", icb_session.sales_tax, "", icb_session.current_time_display[0], icb_session.current_time_display[0])

    icb_session.current_console_messages = icb_session.console_log(message=f"Saved database properties for {icb_session.business_name}. Owner: {icb_session.owner_name}",current_console_messages=icb_session.current_console_messages)


    #9 Create the SKU Table
    sku_repo = SkuRepository(icb_session.connection)
    created_table = sku_repo.create_table()
    #print("SKU_Table")
    print(created_table)




    #Condition Save Location
    icb_session.database_loaded = True
    icb_session.save_location = values[f"-Save_Location_{num}-"]
    #print(f"""The value of save location is: {values['-Save_Location-']}""")
    if len(values[f'-Save_Location_{num}-']) == 0: 
        icb_session.save_location = "./"
        
    elif values[f'-Save_Location_{num}-'] == "/":
        
        icb_session.save_location = "./"
    else:
        icb_session.save_location = values[f'-Save_Location_{num}-']

    #Load to memory
    icb_session.connection = db.load_db_to_memory(icb_session.connection)
    print(f"connection: {icb_session.connection}")

    #Update the dashboard
    window, chart_of_accounts_display_content = update_dashboard_statistics(icb_session.window, values)
    
    #encrypt the database during the session
    icb_session.filekey, icb_session.filename, icb_session.save_location = db.encrypt_database(icb_session.db_name,"encrypt",False, icb_session.save_location, False)

    return icb_session.filekey, icb_session.filename, chart_of_accounts_display_content
    

def update_dashboard_statistics(window, values):
    #this_year = f"tbl_ledger_{icb_session.db_name[:-4]}_{values['-Year_Picker-']}" #Comment out the year picker
    #Bring the user to the dashboard
    this_tab_index = 0
    for i in range(len(tab_keys)):
        if i == this_tab_index:
            window[tab_keys[i]].update(visible=True)
            window[tab_keys[i]].select()
        else:
            window[tab_keys[i]].update(visible=False)
    #Set the time range (default = current YTD)
    #current_year = datetime.datetime.now().year
    #start_date = f"{(icb_session.current_year)}-01-01"
    #end_date = f"{(icb_session.current_year)+1}-01-01"

    #Read the database
    read_ledger_query = f"""SELECT * FROM {icb_session.ledger_name} ORDER BY Transaction_Date;""" # WHERE Transaction_Date >= '{start_date}' AND Transaction_Date < '{end_date}'
    #print(read_ledger_query)
    current_year_ledger = db.execute_read_query_dict(icb_session.connection, read_ledger_query)
    #print(type(current_year_ledger))
    #print(f"read the ledger: {current_year_ledger}")
    if type(current_year_ledger) == str:
        current_year_ledger = False
    repo = AccountRepository(icb_session.connection)
    accounts = repo.get_all()
    #print(accounts)
    #Create and display the chart of accounts.


    #Create and display the key dashboard outputs
    total_debits = 0
    total_credits = 0
    total_balance = 0
    total_assets = 0
    total_expenses = 0
    total_withdrawals = 0
    total_liabilities = 0
    owner_equity = 0
    total_revenue = 0
    if current_year_ledger:
        for transaction in current_year_ledger:
            this_amount = transaction['Amount']
            total_debits = total_debits + this_amount
            total_credits = total_credits + this_amount
            if int(str(transaction['Debit_Acct'])[1]) == 0:
                total_assets = total_assets + this_amount
            if int(str(transaction['Credit_Acct'])[1]) == 0:
                total_assets = total_assets - this_amount
            if int(str(transaction['Debit_Acct'])[1]) == 1:
                total_expenses = total_expenses + this_amount
            if int(str(transaction['Credit_Acct'])[1]) == 1:
                total_expenses = total_expenses - this_amount
            if int(str(transaction['Debit_Acct'])[1]) == 2:
                total_withdrawals = total_withdrawals + this_amount
            if int(str(transaction['Credit_Acct'])[1]) == 2:
                total_withdrawals = total_withdrawals - this_amount
            if int(str(transaction['Credit_Acct'])[1]) == 3:
                total_liabilities = total_liabilities + this_amount
            if int(str(transaction['Debit_Acct'])[1]) == 3:
                total_liabilities = total_liabilities - this_amount
            if int(str(transaction['Credit_Acct'])[1]) == 4:
                owner_equity = owner_equity + this_amount
            if int(str(transaction['Debit_Acct'])[1]) == 4:
                owner_equity = owner_equity - this_amount        
            if int(str(transaction['Credit_Acct'])[1]) == 5:
                total_revenue = total_revenue + this_amount
            if int(str(transaction['Debit_Acct'])[1]) == 5:
                total_revenue = total_revenue - this_amount    
    net_assets = total_assets - total_liabilities
    total_equity = owner_equity + total_revenue - total_expenses - total_withdrawals
    retained_earnings = total_revenue - total_expenses - total_withdrawals
    business_income = total_revenue - total_expenses
    balance = total_debits - total_credits
    
    #Use this format to display the number of cents as dollars
    #total_debits_display = f"{round(total_debits,2)/100}"[:-2] + f"{round(total_debits,2)/100}"[-2:]


    total_debits_display = format_currency(total_debits)
    total_credits_display = format_currency(total_credits)


    total_balance_display = format_currency(total_balance)
    total_assets_display = format_currency(total_assets)
    total_expenses_display = format_currency(total_expenses)
    total_withdrawals_display = format_currency(total_withdrawals)
    total_liabilities_display = format_currency(total_liabilities)
    owner_equity_display = format_currency(owner_equity)
    total_revenue_display = format_currency(total_revenue)    
    total_equity_display = format_currency(total_equity)  
    net_assets_display = format_currency(net_assets) 
    retained_earnings_display = format_currency(retained_earnings) 
    business_income_display = format_currency(business_income) 


    #Balance report
    balance_report = f"""Credits: {total_credits_display}; Debits: {total_debits_display}"""
    window["-Balance_Report-"].update(balance_report)
    if total_credits != total_debits:
        window["-Balance_Message-"].update("Warning: Your accounts are out of balance!")
    
    #assets report
    assets_report = f"""Total Assets: {total_assets_display}"""
    window["-Assets_Report-"].update(assets_report)

    expenses_report = f"""Total Expenses: {total_expenses_display}"""
    window["-Expenses_Report-"].update(expenses_report)

    withdrawals_report = f"""Total Withdrawals: {total_withdrawals_display}"""
    window["-Withdrawals_Report-"].update(withdrawals_report)

    liabilities_report = f"""Total Liabilities: {total_liabilities_display}"""
    window["-Liabilities_Report-"].update(liabilities_report)

    owner_equity_report = f"""Owner Equity: {owner_equity_display}"""
    window["-Equity_Report-"].update(owner_equity_report)

    total_equity_report = f"""Total Equity: {total_equity_display}"""
    window["-Total_Equity_Report-"].update(total_equity_report)

    revenue_report = f"""Revenue: {total_revenue_display}"""
    window["-Revenue_Report-"].update(revenue_report)

    net_assets_report = f"""Net Assets: {net_assets_display}"""
    window["-Net_Assets_Report-"].update(net_assets_report)

    retained_earnings_report = f"""Retained Earnings: {retained_earnings_display}"""
    window["-Retained_Earnings_Report-"].update(retained_earnings_report)

    business_income_report = f"""Business Income: {business_income_display}"""
    window["-Business_Income_Report-"].update(business_income_report)

    window["-Load_Messages-"].update(f"{icb_session.db_name[:-4]}")
    
    window["-Chart_Of_Accounts_Header-"].update(f"{icb_session.db_name[:-4]} Loaded")

    latest_year = window["-Account_Year_Picker-"].Values[-1] #Comment out the year picker

    years = ["All Years"]

    for transaction in current_year_ledger:
        this_year = f"{transaction['Transaction_Date'][:4]}"
        already_year = False
        for year in years:
            if this_year == year:
                already_year = True
        if already_year == False:
            years.append(this_year)
    #print(years)
    window['-Account_Year_Picker-'].update(latest_year, values=years)
    acct_types = values['-Account_Type_Picker-'][:2]
    year = values['-Account_Year_Picker-']
    chart_of_accounts_display_content = update_chart_of_accounts(window, values, acct_types, year)


    return window, chart_of_accounts_display_content







def load_database_properties_tab(window, values, connection):
    if connection==False:
        print("Error: load_database_properties_tab did not execute. Not connected to database.")
    else:

        property_repo = PropertyRepository(connection)

        window['-edit_db_name-'].update(property_repo.get("Business Name") or "")
        window['-Edit_Business_Address-'].update(property_repo.get("Address") or "")
        window['-Edit_Business_Officer-'].update(property_repo.get("Owner or Financial Officer Name") or "")
        window['-Edit_Business_Officer_Title-'].update(property_repo.get("Title or Position") or "")
        window['-Edit_Business_Phone-'].update(property_repo.get("Phone Number") or "")
        window['-Edit_Business_Email-'].update(property_repo.get("Email") or "")
        window['-Edit_Business_Notes-'].update(property_repo.get("Notes") or "")
        window['-Edit_Business_EIN-'].update(property_repo.get("EIN or SSN") or "")
        window['-Edit_Receipts_Repository-'].update(property_repo.get("Receipts Repository Location") or "")
        
        sales_tax = property_repo.get("Sales Tax")
        if sales_tax:
            window['-Edit_Sales_Tax-'].update(f"{dec(sales_tax)*100}")

def load_view_account_tab(window, values, account_number, ledger_name):
    """Loads the selected account from the chart of accounts."""
    repo = AccountRepository(icb_session.connection)
    this_account = repo.get_by_id(account_number)
    

    icb_session.account_number = this_account

    this_account_transactions_query = f"""SELECT * FROM {ledger_name} WHERE Debit_Acct IS {account_number} OR Credit_Acct IS {account_number} ORDER BY Transaction_Date DESC, Transaction_ID DESC;"""
    this_account_transactions = db.execute_read_query_dict(icb_session.connection, this_account_transactions_query)
    this_account_transactions = list(reversed(this_account_transactions))
    #print(this_account_transactions)


    this_account_debits = int(0)
    this_account_credits = int(0)
    this_account_balance = int(0)

    sign_convention = 1
    display_transactions = []
    if len(this_account_transactions)>0:
        
        if int(f"{account_number}"[1]) >2:
            sign_convention = -1
        for transaction in this_account_transactions:
            transaction_amount = format_currency(int(transaction["Amount"]))
            if f"{transaction['Debit_Acct']}" == f"{account_number}":
                this_account_balance = this_account_balance + int(transaction['Amount'])*sign_convention
                this_account_debits = this_account_debits + int(transaction['Amount'])
                this_account_balance_formatted = format_currency(this_account_balance)
                display_transactions.append([transaction["Transaction_ID"],transaction["Transaction_Date"],transaction["Name"],"$0.00",transaction_amount,this_account_balance_formatted])
            elif f"{transaction['Credit_Acct']}" == f"{account_number}":
                this_account_balance = this_account_balance - int(transaction['Amount'])*sign_convention
                this_account_credits = this_account_credits + int(transaction['Amount'])
                this_account_balance_formatted = format_currency(this_account_balance)
                display_transactions.append([transaction["Transaction_ID"],transaction["Transaction_Date"],transaction["Name"],transaction_amount,"$0.00",this_account_balance_formatted])
            
    this_account_debits_formattted = format_currency(this_account_debits)
    this_account_credits_formattted = format_currency(this_account_credits)
    this_account_balance_formattted = format_currency(this_account_balance)
    
    this_account_type = f"{this_account['Account_ID']}"[1]

    if this_account_type == "0":
        this_account_type = "10: Asset"
    elif this_account_type == "1":
        this_account_type = "11: Expenses"
    elif this_account_type == "2":
        this_account_type = "12: Equity Withdrawals"
    elif this_account_type == "3":
        this_account_type = "13: Liabilities"
    elif this_account_type == "4":
        this_account_type = "14: Owner Equity"
    elif this_account_type == "5":
        this_account_type = "15: Revenue"


    #print(this_account)
    window['-Edit_Account_Button-'].update(disabled=False)
    window['-Edit_Account_Number_Input-'].update(this_account['Account_ID'])
    window['-Edit_Account_Name_Input-'].update(this_account['Name'])
    window['-Edit_Account_Type-'].update(this_account_type)
    window['-Edit_Account_Bank-'].update(this_account['Institution'])
    window['-Edit_Account_Bank_Acct_Type-'].update(this_account['Ins_Account_Type'])
    window['-Edit_Account_Bank_Acct_Number-'].update(this_account['Ins_Account_Number'])
    window['-Edit_Account_Bank_Acct_Routing-'].update(this_account['Ins_Routing_Number'])
    window['-Edit_Account_Debits-'].update(f"{this_account_debits_formattted}")
    window['-Edit_Account_Credits-'].update(f"{this_account_credits_formattted}")
    window['-Edit_Account_Balance-'].update(f"{this_account_balance_formattted}")
    window['-Account_Notes_Display-'].update(this_account['Notes'])
    window['-Account_Register_Content-'].update(display_transactions)
    return window, values



def save_account_changes(window, values):
    """Saves account changes to the database."""

    current_time = get_current_time_info()
    
    
    
    
    repo = AccountRepository(icb_session.connection)
    updated_account = repo.update(
        values['-Edit_Account_Number_Input-'],
        values['-Edit_Account_Name_Input-'],
        values['-Account_Notes_Display-'],
        current_time[1],
        values['-Edit_Account_Bank-'],
        values['-Edit_Account_Bank_Acct_Type-'],
        values['-Edit_Account_Bank_Acct_Routing-'],
        values['-Edit_Account_Bank_Acct_Number-']
    )
    icb_session.current_console_messages = icb_session.console_log(f"""Updated Account {values['-Edit_Account_Number_Input-']}; {updated_account}""",icb_session.current_console_messages)
    

def add_vendor_to_database(window,values):
    """Adds a vendor to the database based on the form input."""
    current_time = get_current_time_info()
    add_vendor_number = icb_session.vendor_number
    add_vendor_name = values[f"""-Vendor_Name_{icb_session.num}-"""]
    add_vendor_category = values[f"""-Vendor_Category_{icb_session.num}-"""]
    add_vendor_contact_first = values[f"""-Vendor_Contact_First_{icb_session.num}-"""]
    add_vendor_contact_last = values[f"""-Vendor_Contact_Last_{icb_session.num}-"""]
    add_vendor_contact_preferrred = values[f"""-Vendor_Contact_Preferred_{icb_session.num}-"""]
    add_vendor_phone = values[f"""-Vendor_Phone_{icb_session.num}-"""]
    add_vendor_phone_type = values[f"""-Vendor_Phone_Type_{icb_session.num}-"""]
    add_vendor_address = values[f"""-Vendor_Address_{icb_session.num}-"""]
    add_vendor_email = values[f"""-Vendor_Email_{icb_session.num}-"""]
    add_vendor_website = values[f"""-Vendor_Website_{icb_session.num}-"""]
    add_vendor_notes = values[f"""-Vendor_Notes_{icb_session.num}-"""]

    vendor_repo = VendorRepository(icb_session.connection)
    added_vendor = vendor_repo.insert(add_vendor_number, add_vendor_name, add_vendor_category, add_vendor_contact_first, add_vendor_contact_last, add_vendor_contact_preferrred, add_vendor_phone, add_vendor_phone_type, current_time[1], current_time[1], add_vendor_address, add_vendor_email, add_vendor_website, add_vendor_notes)

    icb_session.current_console_messages = icb_session.console_log(f"Added Vendor {add_vendor_number}: {added_vendor}",icb_session.current_console_messages)


def load_single_vendor(window,values, vendor):
    vendor_repo = VendorRepository(icb_session.connection)
    retrieved_vendor = [vendor_repo.get_by_id(vendor[0])]
    if type(retrieved_vendor) == str:
        print(retrieved_vendor)
    else:  
        #print("retrieved_vendor[0]")
        #print(retrieved_vendor[0]['Vendor_ID'])
        window['-Vendor_Number_Display-'].update(f"Vendor Number {retrieved_vendor[0]['Vendor_ID']}")
        window['-Vendor_Name_Input-'].update(retrieved_vendor[0]['Business_Name'])
        window['-Vendor_Category_Input-'].update(retrieved_vendor[0]['Merchant_Category'])
        window['-Vendor_Contact_First_Input-'].update(retrieved_vendor[0]['Contact_First_Name'])
        window['-Vendor_Contact_Last_Input-'].update(retrieved_vendor[0]['Contact_Last_Name'])
        window['-Vendor_Contact_Preferred_Input-'].update(retrieved_vendor[0]['Preferred_Name'])
        window['-Vendor_Address_Input-'].update(retrieved_vendor[0]['Business_Address'])
        window['-Vendor_Phone_Input-'].update(retrieved_vendor[0]['Phone_Number'])
        window['-Vendor_PhoneType_Input-'].update(f"{retrieved_vendor[0]['Phone_Number_Type']}")        
        window['-Vendor_Email_Input-'].update(retrieved_vendor[0]['Business_Email'])
        window['-Vendor_Website_Input-'].update(retrieved_vendor[0]['Business_Website'])
        window['-Vendor_Notes_Display-'].update(retrieved_vendor[0]['Notes'])

def load_vendors_tab(window,values):
    """Loads the vendors tab on the gui"""
    icb_session.vendors = []
    search_term = values['-Vendors_Search_Input-']
    vendor_repo = VendorRepository(icb_session.connection)
    retrieved_vendors = vendor_repo.search(search_term)

    window["-Edit_Vendor_Button-"].update("Edit Vendor")

    window["-Vendor_Name_Input-"].update("", disabled=True)
    window["-Vendor_Category_Input-"].update("", disabled=True)
    window["-Vendor_Contact_First_Input-"].update("", disabled=True)
    window["-Vendor_Contact_Last_Input-"].update("", disabled=True)
    window["-Vendor_Contact_Preferred_Input-"].update("", disabled=True)
    window["-Vendor_Address_Input-"].update("", disabled=True)
    window["-Vendor_Phone_Input-"].update("", disabled=True)
    window["-Vendor_PhoneType_Input-"].update("", disabled=True)
    window["-Vendor_Email_Input-"].update("", disabled=True)
    window["-Vendor_Website_Input-"].update("", disabled=True)
    window["-Vendor_Notes_Display-"].update("", disabled=True)


    if len(retrieved_vendors) > 0:
        #print(retrieved_vendors[0]['Vendor_ID'])
        
        for vendor in retrieved_vendors:
            icb_session.vendors.append([f"{vendor['Vendor_ID']}",f"{vendor['Business_Name']}",f"{vendor['Contact_First_Name']} {vendor['Contact_Last_Name']}",f"{vendor['Phone_Number']} ({vendor['Phone_Number_Type']})",f"{vendor['Business_Email']}"])
        
        #print(icb_session.vendors)
    window["-View_Vendors_Content-"].update(icb_session.vendors)


def get_customer(window, values, customer_id):
    """Retrieves customer data from the database."""
    customer_query = f"""SELECT * FROM tbl_Customers WHERE Customer_ID = '{customer_id}';"""
    customer = db.execute_read_query_dict(icb_session.connection,customer_query)
    #print(customer)
    if len(customer) < 1:
        return "None"
    else:
        return customer[0]

def add_customer_to_database(window,values):
    """Adds a customer to the database based on the form input."""
    current_time = get_current_time_info()
    add_customer_number = icb_session.customer_number
    add_customer_company_name = values[f"""-Customer_Name_{icb_session.num}-"""]
    add_customer_contact_first = values[f"""-Customer_Contact_First_{icb_session.num}-"""]
    add_customer_contact_last = values[f"""-Customer_Contact_Last_{icb_session.num}-"""]
    add_customer_contact_preferrred = values[f"""-Customer_Contact_Preferred_{icb_session.num}-"""]
    add_customer_phone = values[f"""-Customer_Phone_{icb_session.num}-"""]
    add_customer_phone_type = values[f"""-Customer_Phone_Type_{icb_session.num}-"""]
    add_customer_address = values[f"""-Customer_Address_{icb_session.num}-"""]
    add_customer_email = values[f"""-Customer_Email_{icb_session.num}-"""]
    add_customer_notes = values[f"""-Customer_Notes_{icb_session.num}-"""]

    customer_repo = CustomerRepository(icb_session.connection)
    added_customer = customer_repo.insert(
        customer_id=add_customer_number,
        company_name=add_customer_company_name,
        first_name=add_customer_contact_first,
        last_name=add_customer_contact_last,
        preferred_name=add_customer_contact_preferrred,
        phone=add_customer_phone,
        phone_type=add_customer_phone_type,
        created_time=current_time[1],
        edited_time=current_time[1],
        address=add_customer_address,
        email=add_customer_email,
        notes=add_customer_notes
    )

    icb_session.current_console_messages = icb_session.console_log(f"Added Customer {add_customer_number}: {added_customer}",icb_session.current_console_messages)


def update_customers_view(window, values):
    """Refreshes the customers view panel."""
    search_term = values['-Customers_Search_Input-']
    customer_repo = CustomerRepository(icb_session.connection)
    customers = customer_repo.search(search_term)
    #print(customers)
    if type(customers) == list:
        icb_session.customers= []        
        for customer in customers:
            invoice_repo = InvoiceRepository(icb_session.connection)
            these_invoices = invoice_repo.get_totals_by_customer_and_status(customer['Customer_ID'], ['Due', 'Overdue'])
            balance = 0
            for invoice in these_invoices:
                total = f"{invoice['Total']}".replace("$","")
                total = f"{total}".replace(",","")
                balance = balance + int(dec(total)*100)
            icb_session.customers.append([f"{customer['Customer_ID']}",f"{customer['Customer_Company_Name']}",f"{customer['Customer_First_Name']} {customer['Customer_Last_Name']}",f"{customer['Customer_Phone_Number']}",f"{customer['Customer_Email']}", f"{format_currency(balance)}"])
        icb_session.window["-View_Customers_Content-"].update(icb_session.customers)
        window['-Customer_Name_Input-'].update("")
        window['-Customer_Contact_First_Input-'].update("")
        window['-Customer_Contact_Last_Input-'].update("")
        window['-Customer_Contact_Preferred_Input-'].update("")
        window['-Customer_Address_Input-'].update("")
        window['-Customer_Phone_Input-'].update("")
        window['-Customer_PhoneType_Input-'].update("")        
        window['-Customer_Email_Input-'].update("")
        window['-Customer_Notes_Display-'].update("")    



def load_single_customer(window, values, customer_id):
    """Loads a single customer into the side panel."""
    this_customer_query = f"""Select * FROM tbl_Customers WHERE Customer_ID = '{customer_id[0]}';"""
    retrieved_customer = db.execute_read_query_dict(icb_session.connection,this_customer_query)
    if type(retrieved_customer) == str:
        print(retrieved_customer)
    else:  
        #print("retrieved_customer[0]")
        #print(retrieved_customer[0]['Customer_ID'])
        window['-Customer_Number_Display-'].update(f"Customer Number {retrieved_customer[0]['Customer_ID']}")
        window['-Customer_Name_Input-'].update(retrieved_customer[0]['Customer_Company_Name'])
        window['-Customer_Contact_First_Input-'].update(retrieved_customer[0]['Customer_First_Name'])
        window['-Customer_Contact_Last_Input-'].update(retrieved_customer[0]['Customer_Last_Name'])
        window['-Customer_Contact_Preferred_Input-'].update(retrieved_customer[0]['Preferred_Name'])
        window['-Customer_Address_Input-'].update(retrieved_customer[0]['Customer_Address'])
        window['-Customer_Phone_Input-'].update(retrieved_customer[0]['Customer_Phone_Number'])
        window['-Customer_PhoneType_Input-'].update(f"{retrieved_customer[0]['Customer_Phone_Number_Type']}")        
        window['-Customer_Email_Input-'].update(retrieved_customer[0]['Customer_Email'])
        window['-Customer_Notes_Display-'].update(retrieved_customer[0]['Notes'])    





def load_ledger_tab(window, values):
    """Loads transactions into the Ledger."""
    selected_year = values['-Ledger_Year_Picker-']


    years = ["All Years"]
    get_ledger_query = f"""SELECT Transaction_Date FROM {icb_session.ledger_name};"""
    current_ledger = db.execute_read_query_dict(icb_session.connection,get_ledger_query)
    for transaction in current_ledger:
        this_year = f"{transaction['Transaction_Date'][:4]}"
        already_year = False
        for year in years:
            if this_year == year:
                already_year = True
        if already_year == False:
            years.append(this_year)
    #print(years)
    window['-Ledger_Year_Picker-'].update("All Years",values=years)
    window['-Ledger_Search_Input-'].update("")
    transactions_query = ""
    if selected_year == "All Years":
        transactions_query = f"""SELECT * FROM {icb_session.ledger_name} WHERE Transaction_ID 
        = '{values['-Ledger_Search_Input-']}' OR Name LIKE '%{values['-Ledger_Search_Input-']}%' OR Amount LIKE '%{values['-Ledger_Search_Input-']}%'  
        OR Credit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' OR Debit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' 
        OR Amount LIKE '%{convert_dollars_to_cents(values['-Ledger_Search_Input-'])}%' OR Notes LIKE '%{values['-Ledger_Search_Input-']}%' 
        OR Vendor = '{values['-Ledger_Search_Input-']}' 
        OR Customer = '{values['-Ledger_Search_Input-']}' ORDER BY Transaction_ID DESC;"""
    else:
        transactions_query = f"""SELECT * FROM {icb_session.ledger_name} WHERE Transaction_ID 
        = '{values['-Ledger_Search_Input-']}' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Name LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Amount LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' 
        OR Credit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Debit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' 
        OR Amount LIKE '%{convert_dollars_to_cents(values['-Ledger_Search_Input-'])}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Notes LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{current_year}-01-01' 
        OR Vendor = '{values['-Ledger_Search_Input-']}' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' 
        OR Customer = '{values['-Ledger_Search_Input-']}' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' ORDER BY Transaction_ID DESC;"""
    #print(transactions_query)
    icb_session.transactions = []
    #print(icb_session.transactions)
    these_transactions = db.execute_read_query_dict(icb_session.connection,transactions_query)
    #print(these_transactions)
    if len(these_transactions) > 0 and type(these_transactions) == list:        
        for transaction in these_transactions:
            retrieved_customer = get_customer(icb_session.window,values,transaction['Customer'])
            customer_name = "None"
            if retrieved_customer != "None":
                #print(retrieved_customer)
                customer_name = f"{retrieved_customer['Customer_First_Name']} {retrieved_customer['Customer_Last_Name']} ({retrieved_customer['Preferred_Name']})"
            
            icb_session.transactions.append([f"{transaction['Transaction_ID']}",f"{transaction['Name']}",f"{format_currency(int(transaction['Amount']))}",f"{transaction['Debit_Acct']}",f"{transaction['Credit_Acct']}", f"{transaction['Transaction_Date']}"])
        icb_session.window["-Ledger_Display_Content-"].update(icb_session.transactions)
        icb_session.window['-Ledger_Title_Display-'].update(icb_session.ledger_name)
    

    else:
        #icb_session.transactions = []
        icb_session.current_console_messages = icb_session.console_log("Add a new Transaction to the database to get started.",icb_session.current_console_messages)
    window['-Ledger_Name_Input-'].update("", readonly=True)
    window['-Ledger_Date_Input-'].update("", readonly=True)
    window['-Ledger_Recorded_Input-'].update("", readonly=True)
    window['-Ledger_Edited_Input-'].update("", readonly=True)
    window['-Ledger_Amount_Input-'].update("", readonly=True)
    window['-Ledger_Credit_Input-'].update("", readonly=True)
    window['-Ledger_Debit_Input-'].update("", readonly=True)
    window['-Ledger_Customer_Input-'].update("", readonly=True)
    window['-Ledger_Vendor_Input-'].update("", readonly=True)
    window["-Transaction_Image_Button-"].update("Record")
    window['-Transaction_Notes_Display-'].update("", disabled=True)
    window['-Transaction_Number_Display-'].update("Transaction Number")


def search_ledger(window,values):
    """Loads transactions into the Ledger."""
    selected_year = values['-Ledger_Year_Picker-']



    transactions_query = ""
    if selected_year == "All Years":
        transactions_query = f"""SELECT * FROM {icb_session.ledger_name} WHERE Transaction_ID 
        = '{values['-Ledger_Search_Input-']}' OR Name LIKE '%{values['-Ledger_Search_Input-']}%' OR Amount LIKE '%{values['-Ledger_Search_Input-']}%'  
        OR Credit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' OR Debit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' 
        OR Amount LIKE '%{convert_dollars_to_cents(values['-Ledger_Search_Input-'])}%' OR Notes LIKE '%{values['-Ledger_Search_Input-']}%' 
        OR Vendor = '{values['-Ledger_Search_Input-']}' 
        OR Customer = '{values['-Ledger_Search_Input-']}' ORDER BY Transaction_ID DESC;"""
    else:
        transactions_query = f"""SELECT * FROM {icb_session.ledger_name} WHERE Transaction_ID 
        = '{values['-Ledger_Search_Input-']}' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Name LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Amount LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' 
        OR Credit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Debit_Acct LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' 
        OR Amount LIKE '%{convert_dollars_to_cents(values['-Ledger_Search_Input-'])}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' OR Notes LIKE '%{values['-Ledger_Search_Input-']}%' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{current_year}-01-01' 
        OR Vendor = '{values['-Ledger_Search_Input-']}' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' 
        OR Customer = '{values['-Ledger_Search_Input-']}' AND Transaction_Date <= '{selected_year}-12-31' AND Transaction_Date >= '{selected_year}-01-01' ORDER BY Transaction_ID DESC;"""
    #print(transactions_query)
    icb_session.transactions = []
    #print(icb_session.transactions)
    these_transactions = db.execute_read_query_dict(icb_session.connection,transactions_query)
    #print(these_transactions)
    if len(these_transactions) > 0 and type(these_transactions) == list:        
        for transaction in these_transactions:
            retrieved_customer = get_customer(icb_session.window,values,transaction['Customer'])
            customer_name = "None"
            if retrieved_customer != "None":
                #print(retrieved_customer)
                customer_name = f"{retrieved_customer['Customer_First_Name']} {retrieved_customer['Customer_Last_Name']} ({retrieved_customer['Preferred_Name']})"
            
            icb_session.transactions.append([f"{transaction['Transaction_ID']}",f"{transaction['Name']}",f"{format_currency(int(transaction['Amount']))}",f"{transaction['Debit_Acct']}",f"{transaction['Credit_Acct']}", f"{transaction['Transaction_Date']}"])
        icb_session.window["-Ledger_Display_Content-"].update(icb_session.transactions)
        icb_session.window['-Ledger_Title_Display-'].update(icb_session.ledger_name)
    

    else:
        #icb_session.transactions = []
        icb_session.current_console_messages = icb_session.console_log("Add a new Transaction to the database to get started.",icb_session.current_console_messages)
    window['-Ledger_Name_Input-'].update("", readonly=True)
    window['-Ledger_Date_Input-'].update("", readonly=True)
    window['-Ledger_Recorded_Input-'].update("", readonly=True)
    window['-Ledger_Edited_Input-'].update("", readonly=True)
    window['-Ledger_Amount_Input-'].update("", readonly=True)
    window['-Ledger_Credit_Input-'].update("", readonly=True)
    window['-Ledger_Debit_Input-'].update("", readonly=True)
    window['-Ledger_Customer_Input-'].update("", readonly=True)
    window['-Ledger_Vendor_Input-'].update("", readonly=True)
    window["-Transaction_Image_Button-"].update("Record")
    window['-Transaction_Notes_Display-'].update("", disabled=True)
    window['-Transaction_Number_Display-'].update("Transaction Number")



def load_transaction_details(transaction_number):
    #print(transaction_number)
    #transaction_number = int(transaction_number[0]+1)
    retrieve_transaction_query = f"""SELECT * FROM {icb_session.ledger_name} WHERE Transaction_ID = {transaction_number};"""
    transaction = db.execute_read_query_dict(icb_session.connection,retrieve_transaction_query)
    icb_session.window['-Transaction_Number_Display-'].update(f"Transaction {transaction[0]['Transaction_ID']}")
    icb_session.window['-Ledger_Name_Input-'].update(f"{transaction[0]['Name']}")
    icb_session.window['-Ledger_Date_Input-'].update(f"{transaction[0]['Transaction_Date']}")
    icb_session.window['-Ledger_Recorded_Input-'].update(f"{transaction[0]['Created_Time']}")
    icb_session.window['-Ledger_Edited_Input-'].update(f"{transaction[0]['Edited_Time']}")
    icb_session.window['-Ledger_Amount_Input-'].update(f"{format_currency(transaction[0]['Amount'])}")
    icb_session.window['-Ledger_Credit_Input-'].update(f"{transaction[0]['Credit_Acct']}")
    icb_session.window['-Ledger_Debit_Input-'].update(f"{transaction[0]['Debit_Acct']}")
    icb_session.window['-Ledger_Recorded_Input-'].update(f"{transaction[0]['Created_Time']}")
    icb_session.window['-Ledger_Customer_Input-'].update(f"{transaction[0]['Customer']}")
    icb_session.window['-Ledger_Vendor_Input-'].update(f"{transaction[0]['Vendor']}")
    icb_session.window['-Transaction_Notes_Display-'].update(f"{transaction[0]['Notes']}")
    #print(transaction[0]['Record_Image'])
    icb_session.window['-Transaction_Image_Button-'].update(f"{transaction[0]['Record_Image']}")


def add_transaction_to_database(values):
    """Adds a transaction to the database."""
    current_time = get_current_time_info()

    #print(icb_session.transaction_date)
    this_credit_account = int(values[f'-Transaction_Credit_Account_{icb_session.num}-'][0:5])
    this_debit_account = int(values[f"-Transaction_Debit_Account_{icb_session.num}-"][0:5])
    this_amount = convert_dollars_to_cents(values[f"-Transaction_Amount_{icb_session.num}-"])
    #print("this_amount")
    #print(this_amount)
    this_name = values[f"-Transaction_Name_{icb_session.num}-"]
    this_notes = values[f"-Transaction_Notes_{icb_session.num}-"]
    this_image = values[f"-Transaction_Image_Input_{icb_session.num}-"]
    if this_image[-4:] == ".pdf":
        this_image = this_image[:-4]+'_0.png'
    this_vendor = values[f"-Transaction_Vendor_{icb_session.num}-"][:f"{values[f"-Transaction_Vendor_{icb_session.num}-"]}".find(" ")]
    #this_customer = values[f"-Transaction_Customer_{icb_session.num}-"]
    this_transaction_date = values[f'-Transaction_Date_String_{icb_session.num}-']
    add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, Edited_Time, Transaction_Date, Record_Image, Vendor)
    VALUES ({this_credit_account},{this_debit_account},{this_amount},"{this_name}","{this_notes}","{current_time[1]}","{current_time[1]}","{this_transaction_date}","{this_image}","{this_vendor}");"""
    #print(add_transaction_query)
    added_transaction = db.execute_query(icb_session.connection,add_transaction_query)
    #print(added_transaction)
    icb_session.current_console_messages = icb_session.console_log(f"Transaction {icb_session.num} Added: {added_transaction}",icb_session.current_console_messages)

def convert_pdf_to_png(image_url):
    """Converts a pdf file to png images. 
    Returns a list of images, each representing a page from the pdf."""
    if image_url[-4:] == ".pdf" :
        print(f"Converting pdf: {image_url}")
        with tempfile.TemporaryDirectory() as path:
            pdf_location = os.path
            #print(pdf_location)
            images_from_path = convert_from_path(image_url, output_folder=path, size=350, paths_only=True, fmt="png")
            #print(images_from_path)
            # Do something here
            remove_to = image_url[::-1].index("/")
            ##print(remove_to)
            image_location = image_url[:len(image_url)-remove_to]
            #print(image_url)
            #print(image_location)
            image_name_0 = image_url[-remove_to:]            
            image_name = image_name_0[:-4]
            #print(image_name)
            new_images = []
            for i in range(len(images_from_path)):
                new_image = f"{image_location}/{image_name}_{i}.png"
                shutil.copyfile(images_from_path[i],new_image)
                new_images.append(new_image)
            return new_images
    else:
        return "Error: File is not a pdf"

def add_account_to_database(values):
    """Adds an account with an account number based on the account type as indicated by characters [:2].
    10: Asset Accounts
    11: Expenese Accounts
    12: Equity Withdrawal Accounts
    13: Liability Accounts
    14: Owner Equity Contribution Accounts
    15: Revenue Accounts"""
    current_time = get_current_time_info()
    #print(current_time)
    account_type = int(values[f'-Account_Type_Picker_{icb_session.num}-'][:2])
    #print(account_type)

    repo = AccountRepository(icb_session.connection)
    account_count_val = repo.get_count_in_range(int(f"{account_type}000"), int(f"{account_type+1}000"))
    #print("account_count")
    #print(account_count_val)
    new_account_number = 0
    if type(new_account_number) != str:
        new_account_number = int(f"{account_type}001") + account_count_val
        #print(count_accounts_query)
        #print("account_number")
        #print(new_account_number)
        account_number_str = ""
        if type(new_account_number) != str:
            account_number_str = f"""{new_account_number}"""
        
        new_account_name = values[f"-Account_Name_{icb_session.num}-"]
        new_account_notes = values[f"-Account_Notes_{icb_session.num}-"]
        new_account_bank = values[f"-Account_Bank_{icb_session.num}-"]
        new_account_bank_type = values[f"-Account_Bank_Account_Type_{icb_session.num}-"]
        new_account_routing = values[f"-Account_Bank_Routing_{icb_session.num}-"]
        new_account_bank_account_number = values[f"-Account_Bank_Account_Number_{icb_session.num}-"]
        created_account = repo.insert(
            new_account_number,
            new_account_name,
            new_account_notes,
            current_time[1],
            current_time[1],
            new_account_bank,
            new_account_bank_type,
            new_account_routing,
            new_account_bank_account_number
        )
        icb_session.current_console_messages = icb_session.console_log(message=created_account,current_console_messages=icb_session.current_console_messages)
        print(created_account)
    else:
        icb_session.current_console_messages = icb_session.console_log(message=account_count_val,current_console_messages=icb_session.current_console_messages)


def update_chart_of_accounts(window, values, acct_types, year):
    #if acct_types == "All Accounts" and year == 'All Years':
    #    update_dashboard_statistics(window,values)
    #else:
    if acct_types == "Al":
        acct_types = ""
    read_ledger_query = f"""SELECT * FROM {icb_session.ledger_name} WHERE Credit_Acct LIKE '{acct_types}%' """
    #Read the database
    if year != "All Years" and acct_types == "11" or year != "All Years" and acct_types == "12" or year != "All Years" and acct_types == "15":
        #print(year)
        read_ledger_query = read_ledger_query + f""" AND Transaction_Date >= '{year}-01-01' AND Transaction_Date <= '{year}-12-31' OR Debit_Acct LIKE '{acct_types}%' AND Transaction_Date >= '{year}-01-01' AND Transaction_Date <= '{year}-12-31';"""
    elif year != "All Years" and acct_types == "10" or year != "All Years" and acct_types == "13" or year != "All Years" and acct_types == "14" or year != "All Years" and acct_types == "":
        read_ledger_query = read_ledger_query + f""" AND Transaction_Date <= '{year}-12-31' OR Debit_Acct LIKE '{acct_types}%' AND Transaction_Date <= '{year}-12-31';"""        
    else:
        read_ledger_query = read_ledger_query + f"""OR Debit_Acct LIKE '{acct_types}%';"""

    #read_ledger_query = f"""SELECT * FROM {icb_session.ledger_name};""" # WHERE Transaction_Date >= '{start_date}' AND Transaction_Date < '{end_date}'
    #print(read_ledger_query)
    current_year_ledger = db.execute_read_query_dict(icb_session.connection, read_ledger_query)
    #print(type(current_year_ledger))
    #print(f"read the ledger: {current_year_ledger}")
    if type(current_year_ledger) == str:
        current_year_ledger = False
    repo = AccountRepository(icb_session.connection)
    accounts = repo.get_by_type_prefix(acct_types)
    #print(accounts)
    #Create and display the chart of accounts.
    chart_of_accounts_display_content = []
    for account in accounts:
        account_type = 1
        account_Id = str(account['Account_ID'])
        account_Name = str(account['Name'])
        account_category = f"{account['Account_ID']}"[:2]
        #print(account_Id)
        if int(account_Id[1]) >= 3:
            account_type = int(-1)
        credits = 0
        debits = 0
        balance = 0
        if current_year_ledger:
            for transaction in current_year_ledger:
                transaction_Id = transaction['Transaction_ID']
                debit_account = transaction['Debit_Acct']
                credit_account = transaction['Credit_Acct']
                amount = transaction['Amount']
                if debit_account == account_Id and transaction['Transaction_Date'][:4] == year or debit_account == account_Id and year == "All Years" or debit_account == account_Id and account_category == "10" or debit_account == account_Id and account_category == "13" or debit_account == account_Id and account_category == "14":
                    debits = debits + amount
                    balance = account_type*(debits - credits)
                elif credit_account == account_Id and transaction['Transaction_Date'][:4] == year or credit_account == account_Id and year == "All Years" or credit_account == account_Id and account_category == "10" or credit_account == account_Id and account_category == "13" or credit_account == account_Id and account_category == "14":
                    credits = credits + amount
                    balance = account_type*(debits - credits)
        credits =  format_currency(credits)
        debits = format_currency(debits)
            
        balance = format_currency(balance)
        
        chart_of_accounts_display_content.append([account_Id,account_Name,credits, debits, balance])
    window['-Chart_of_Accounts_Content-'].update(chart_of_accounts_display_content)        
    return chart_of_accounts_display_content


def update_pos_view(window,values):
    """Refreshes the pos view panel."""
    search_term = values['-POS_Search_Input-']
    invoice_repo = InvoiceRepository(icb_session.connection)
    customer_repo = CustomerRepository(icb_session.connection)

    customers = customer_repo.search(search_term)
    #print(customers[0]['Customer_ID'])
    if len(customers) > 0:


        icb_session.invoices= []  
        for customer in customers:
            invoices = invoice_repo.get_by_customer_id(customer['Customer_ID'])
            #print(invoices)
            if len(invoices) > 0 and type(invoices) == list:
                for invoice in invoices:
                    icb_session.invoices.append([f"{invoice['Invoice_ID']}",f"{customer['Customer_First_Name']} {customer['Customer_Last_Name']}",f"{customer['Customer_Phone_Number']}",f"{customer['Customer_Email']}",f"{invoice['Total']}", f"{invoice['Status']}"])
                icb_session.invoices.sort(reverse=True)
            icb_session.window["-View_POS_Content-"].update(icb_session.invoices)
    else:
        icb_session.invoices= []  
        invoices = invoice_repo.search(search_term)
        #print(invoices)
        if len(invoices) > 0 and type(invoices) == list:
            for invoice in invoices:
                customer = [customer_repo.get_by_id(invoice['Customer_ID'])]
                icb_session.invoices.append([f"{invoice['Invoice_ID']}",f"{customer[0]['Customer_First_Name']} {customer[0]['Customer_Last_Name']}",f"{customer[0]['Customer_Phone_Number']}",f"{customer[0]['Customer_Email']}",f"{invoice['Total']}", f"{invoice['Status']}"])
                icb_session.window["-View_POS_Content-"].update(icb_session.invoices)
    window['-POS_Number_Display-'].update(f"Invoice Number")
    window['-POS_CustomerName_Input-'].update("")
    window['-POS_CustomerContact_Input-'].update(f"""""")
    window['-POS_CustomerEmail_Input-'].update("")
    window['-POS_CustomerPhone_Input-'].update("")
    window['-POS_TrackingCode_Input-'].update("")
    window['-POS_Subtotal_Input-'].update(f"")
    window['-POS_SalesTax_Input-'].update(f"")
    window['-POS_Total_Input-'].update(f"")
    window['-POS_DueDate_Input-'].update(f"")
    window['-POS_Status_Input-'].update("")
    window['-Edit_POS_Button-'].update("Edit Invoice")


def load_single_invoice(window, values, invoice_id):
    """Loads a single invoice into the side panel."""
    invoice_repo = InvoiceRepository(icb_session.connection)
    icb_session.this_invoice = invoice_repo.get_by_id(invoice_id)
    
    if icb_session.this_invoice is None:
        print("retrieved invoice is None")
    elif type(icb_session.this_invoice) == str:
        print("retrieved invoice error: " + icb_session.this_invoice)
    else:  
        customer_repo = CustomerRepository(icb_session.connection)
        this_customer = [customer_repo.get_by_id(icb_session.this_invoice['Customer_ID'])]
        if type(this_customer) == str:
            print(this_customer)
        else:  
            window['-POS_Number_Display-'].update(f"Invoice {icb_session.this_invoice['Invoice_ID']}")
            window['-POS_CustomerName_Input-'].update(this_customer[0]['Customer_Company_Name'])
            window['-POS_CustomerContact_Input-'].update(f"""{this_customer[0]['Customer_First_Name']} {this_customer[0]['Customer_Last_Name']}""")
            window['-POS_CustomerEmail_Input-'].update(this_customer[0]['Customer_Email'])
            window['-POS_CustomerPhone_Input-'].update(this_customer[0]['Customer_Phone_Number'])
            window['-POS_TrackingCode_Input-'].update(icb_session.this_invoice['Tracking_Code'])
            window['-POS_Subtotal_Input-'].update(f"{icb_session.this_invoice['Subtotal']}")
            window['-POS_SalesTax_Input-'].update(f"{icb_session.this_invoice['Sales_Tax']}")
            window['-POS_Total_Input-'].update(f"{icb_session.this_invoice['Total']}")
            window['-POS_DueDate_Input-'].update(f"{icb_session.this_invoice['Due_Date']}")
            window['-POS_Status_Input-'].update(icb_session.this_invoice['Status'])
            window['-View_POS_Button-'].update(f"{icb_session.this_invoice['Location']}")


def add_service_to_database(window,values):
    """Adds a service to the database based on the form input."""
    current_time = get_current_time_info()
    add_service_number = icb_session.service_number
    add_service_description = values[f"""-Service_Description_{icb_session.num}-"""]
    add_service_long_description = values[f"""-Service_Long_Description_{icb_session.num}-"""]
    #add_service_photo = "none"#values[f"""-Service_Photo_{icb_session.num}-"""]
    price_input = values[f"""-Service_Price_{icb_session.num}-"""]
    price_input = f"{price_input}".replace("$", "")
    add_service_price= convert_dollars_to_cents(price_input)
    add_service_taxable = values[f"""-Service_Taxable_{icb_session.num}-"""]
    sku_repo = SkuRepository(icb_session.connection)
    added_service = sku_repo.insert(add_service_number, add_service_description.replace("'","''"), add_service_long_description, add_service_price, add_service_taxable, "False", "Service", current_time[1], current_time[1])
    icb_session.current_console_messages = icb_session.console_log(f"Added Service {add_service_number}: {added_service}",icb_session.current_console_messages)

def load_services_tab(window,values):
    """Refreshes the services view panel."""
    search_term = values['-Services_Search_Input-']
    sku_repo = SkuRepository(icb_session.connection)
    services = sku_repo.get_services(search_term)
    #print(services)
    if type(services) == list:
        icb_session.services= []        
        for service in services:
            icb_session.services.append([f"{service['Sku']}",f"{service['Description']}",f"{format_currency(service['Price'])}",f"{service['Taxable']}"])
        icb_session.window["-View_Services_Content-"].update(icb_session.services)
        window['-Service_Sku_Input-'].update("")
        window['-Service_Description_Input-'].update("")
        window['-Service_Price_Input-'].update("")
        window['-Service_Taxable_Input-'].update("")
        window['-Service_Notes_Display-'].update("")
        window["-Edit_Service_Button-"].update("Edit SKU")
        window["-Service_Sku_Input-"].update(disabled=True)
        window["-Service_Description_Input-"].update(disabled=True)
        window["-Service_Price_Input-"].update(disabled=True)
        window["-Service_Taxable_Input-"].update(disabled=True)
        window["-Service_Notes_Display-"].update(disabled=True)

def load_single_service(window, values, service_id):
    """Loads a single service into the side panel."""
    sku_repo = SkuRepository(icb_session.connection)
    retrieved_service = [sku_repo.get_by_sku(service_id[0])]
    if type(retrieved_service) == str:
        print(retrieved_service)
    else:  
        #print("retrieved_service[0]")
        #print(retrieved_service[0]['Sku_ID'])
        window['-Service_Sku_Input-'].update(retrieved_service[0]['Sku'])
        window['-Service_Description_Input-'].update(retrieved_service[0]['Description'])
        window['-Service_Price_Input-'].update(format_currency(retrieved_service[0]['Price']))
        window['-Service_Taxable_Input-'].update(retrieved_service[0]['Taxable'])
        window['-Service_Notes_Display-'].update(retrieved_service[0]['Long_Description'])

def activate_edit_transaction_fields(window,values):

    if window["-Edit_Transaction_Button-"].get_text() == "Edit Transaction":

        window['-Ledger_Name_Input-'].update(disabled=False)
        window['-Ledger_Date_Input-'].update(disabled=False)
        window['-Ledger_Amount_Input-'].update(disabled=False)
        window['-Ledger_Credit_Input-'].update(disabled=False)
        window['-Ledger_Debit_Input-'].update(disabled=False)
        window['-Ledger_Customer_Input-'].update(disabled=False)
        window['-Ledger_Vendor_Input-'].update(disabled=False)    
        window['-Transaction_Notes_Display-'].update(disabled=False) 
        window["-Edit_Transaction_Button-"].update("Save Transaction")

    elif window["-Edit_Transaction_Button-"].get_text() == "Save Transaction":







        this_transaction = ""

        ledger_content = values['-Ledger_Display_Content-']
        #print(ledger_content)
        if len(ledger_content) != 0:
            this_transaction_index = ledger_content[0]
            this_transaction = icb_session.transactions[this_transaction_index][0]

        amount_int = ""

        if values['-Ledger_Amount_Input-'][0] == "$":
            amount_int = convert_dollars_to_cents(values['-Ledger_Amount_Input-'][1:].replace(",",""))
        else:
            amount_int = convert_dollars_to_cents(values['-Ledger_Amount_Input-'][0:].replace(",",""))
        
        update_transaction_query = f"""UPDATE '{icb_session.ledger_name}' SET Credit_Acct = '{values['-Ledger_Credit_Input-']}', 
        Debit_Acct = '{values['-Ledger_Debit_Input-']}', Amount = '{amount_int}', 
        Notes = '{values['-Transaction_Notes_Display-']}', Transaction_Date = '{values['-Ledger_Date_Input-']}', 
        Vendor = '{values['-Ledger_Vendor_Input-']}', Customer = '{values['-Ledger_Customer_Input-']}', 
        Name = '{values['-Ledger_Name_Input-']}', Edited_Time = '{now}'  WHERE Transaction_ID='{this_transaction}';"""
        query_executed = db.execute_query(icb_session.connection,update_transaction_query)
        icb_session.console_log(query_executed,icb_session.current_console_messages)
        window['-Ledger_Name_Input-'].update(disabled=True)
        window['-Ledger_Date_Input-'].update(disabled=True)
        window['-Ledger_Amount_Input-'].update(disabled=True)
        window['-Ledger_Credit_Input-'].update(disabled=True)
        window['-Ledger_Debit_Input-'].update(disabled=True)
        window['-Ledger_Customer_Input-'].update(disabled=True)
        window['-Ledger_Vendor_Input-'].update(disabled=True) 
        window['-Transaction_Notes_Display-'].update(disabled=True)   
        window["-Edit_Transaction_Button-"].update("Edit Transaction")
        load_ledger_tab(window,values)

def populate_invoice_totals(new_invoice_window,values_newi):

    sales_tax_dec = dec(values_newi[f"-Invoice_SalesTax_Rate_{icb_session.num}-"])/dec(100)
    this_invoice_subtotal = 0
    this_invoice_sales_tax = 0
    for line_item in icb_session.these_line_items:
        this_line_total = int(dec(line_item[4][1:].replace(",",""))*100)
        
        this_invoice_subtotal = this_line_total + this_invoice_subtotal

        this_line_sku = line_item[0]
        sku_repo = SkuRepository(icb_session.connection)
        this_sku = sku_repo.get_by_sku(this_line_sku)
        this_line_taxable = this_sku['Taxable'] if this_sku else "False"
        #print(this_line_taxable)
        if this_line_taxable == "True":
            this_sales_tax = int(dec(line_item[4][1:].replace(",",""))*100)*sales_tax_dec
        
            this_invoice_sales_tax = this_invoice_sales_tax + this_sales_tax
    
    new_invoice_window[f"-Invoice_Subtotal_{icb_session.num}-"].update(format_currency(this_invoice_subtotal))
    new_invoice_window[f"-Invoice_SalesTax_{icb_session.num}-"].update(format_currency(this_invoice_sales_tax))
    new_invoice_window[f"-Invoice_Total_{icb_session.num}-"].update(format_currency(this_invoice_sales_tax+this_invoice_subtotal))





def generate_new_invoice(new_invoice_window, values_newi, date):

    #this_invoice_id = icb_session.this_invoice['Invoice_ID']
    extra_whitespace = "    "
    #this_invoice_text = icb_session.this_invoice['Line_Items']

    #Get the organization Name
    property_repo = PropertyRepository(icb_session.connection)

    #Get the organization Name
    this_org_name = property_repo.get('Business Name') or ""

     #Get the organization CEO
    this_org_ceo = property_repo.get('Owner or Financial Officer Name') or ""

     #Get the organization Address
    this_org_address = property_repo.get('Address') or ""

     #Get the organization Email
    this_org_email = property_repo.get('Email') or ""

     #Get the organization Phone
    this_org_phone = property_repo.get('Phone Number') or ""

    #Get the customer
    get_customer_query = f"""SELECT * FROM tbl_Customers WHERE Customer_ID = '{icb_session.this_invoice['Customer_ID']}';"""
    this_customer = db.execute_read_query_dict(icb_session.connection,get_customer_query)
    #print(f"{this_customer}")
    this_customer = this_customer[0]
    #Create the directory
    filenames = []
    foldername = icb_session.this_invoice['Invoice_ID']
    folderpath = f'{icb_session.receipts_location}/Invoices/{foldername}'
    #Create the invoice directory, if it doesn't already exist
    if os.path.isdir(f'{icb_session.receipts_location}/Invoices') == False:
        os.mkdir(f'{icb_session.receipts_location}/Invoices')
    if os.path.isdir(folderpath) == False:
        os.mkdir(folderpath)
 
    #Check the status and set the date
    invoice_paid_date = icb_session.this_invoice['Due_Date'][:10]
    if icb_session.this_invoice['Status'] == 'Paid' or icb_session.this_invoice['Status'] == 'Refunded' or icb_session.this_invoice['Status'] == 'Canceled':
        invoice_paid_date = f"{now}"[:10]


    #Set text attributes
    small_font = ImageFont.truetype('./fonts/LiberationSerif-Regular.ttf', 50)    
    medium_font = ImageFont.truetype('./fonts/LiberationSerif-Regular.ttf', 70) 
    large_font = ImageFont.truetype('./fonts/LiberationSerif-Regular.ttf', 100)             
    test_canvas = Image.new('RGB', (2550, 3300), "white")
    test_draw = ImageDraw.Draw(test_canvas)
    canvas = Image.new('RGB', (2550, 3300), "white")
    
    draw = ImageDraw.Draw(canvas)
    min_line_width = 1950
    max_line_width = 2150
    target = 2100 
    this_header = "SKU       Description                        Price            Qty           Total"
    #for line_item in icb_session.these_line_items:
    #    this_page = this_page + f"""{line_item[0]}{extra_whitespace}{line_item[1]}{extra_whitespace}{line_item[2]}{extra_whitespace}{line_item[3]}{extra_whitespace}{line_item[4]}{extra_whitespace}""" + "\n"



    filename = f"{icb_session.this_invoice['Invoice_ID']}_0.png"
    #CENTER IS 1275,1650

    #Find the offset for the Org Name
    left_shift = len(this_org_name)*25/2

    #Todo: correct to full justify
    #ImageDraw.textlength() #This will 

    filenames.append(filename)
    #Draw the invoice page
    draw.text((225,225),f"INVOICE {icb_session.this_invoice['Invoice_ID']}{extra_whitespace}                               {date}", '#000000', large_font)    
    
    draw.text((225,425),f"Bill To:\n{this_customer['Customer_Company_Name']}\n{this_customer['Customer_First_Name']} {this_customer['Customer_Last_Name']}\n{this_customer['Customer_Address']}\n{this_customer['Customer_Phone_Number']}\n{this_customer['Customer_Email']}",'#000000',small_font)
    draw.text((1525,425),f"Remit To:\n{this_org_name}\n{this_org_ceo}\n{this_org_address}\n{this_org_phone}\n{this_org_email}",'#000000',small_font)
    
    #Draw the line items
    draw.text((225,925),this_header, '#000000', medium_font)
    num_line_items = len(icb_session.these_line_items)

    for i in range(num_line_items):
        draw.text((225,925+((i+1)*(70+50))),f"{icb_session.these_line_items[i][0]}", '#000000', medium_font)
        draw.text((500,940+((i+1)*(70+50))),f"{icb_session.these_line_items[i][1]}", '#000000', small_font)
        draw.text((1250,925+((i+1)*(70+50))),f"{icb_session.these_line_items[i][2]}", '#000000', medium_font)
        draw.text((1600,925+((i+1)*(70+50))),f"{icb_session.these_line_items[i][3]}", '#000000', medium_font)
        draw.text((1900,925+((i+1)*(70+50))),f"{icb_session.these_line_items[i][4]}", '#000000', medium_font)
    
    draw.text((1630,925+((num_line_items+1)*(70+50))),f"Subtotal: {icb_session.this_invoice['Subtotal']}", '#000000', medium_font)    
    draw.text((1630,925+((num_line_items+2)*(70+50))),f"Tax:        {icb_session.this_invoice['Sales_Tax']}", '#000000', medium_font)    
    draw.text((1630,925+((num_line_items+3)*(70+50))),f"Total:      {icb_session.this_invoice['Total']}", '#000000', medium_font)    
    draw.text((1275-380,2900),f"Status: {icb_session.this_invoice['Status']} {invoice_paid_date}", '#000000', medium_font)    


    draw.text((1275-(20*25),3035),f"{icb_session.this_invoice['Tracking_Code']}",'#000000',small_font)
    draw.text((1275-left_shift,3100),f"{this_org_name}",'#000000',small_font)
    draw.text((1275-(7*25),3165),f"Page 1 of 1",'#000000',small_font)
    


    canvas.save(f'{folderpath}/{filename}', "PNG")
    #img2pdf
        

       #print(f"Generated Page {i+1}")

    # convert all files ending in .png in a directory and its subdirectories tp PDF format
    dirname = folderpath
    images = []
    for r, _, f in os.walk(dirname):
        for fname in f:
            if not fname.endswith(".png"):
                continue
            images.append(os.path.join(r, fname))
    images.sort()
    dpix = dpiy = 300
    this_layout = img2pdf.get_fixed_dpi_layout_fun((dpix, dpiy))
    filepath = f"{folderpath}/{foldername}.pdf"
    with open(filepath,"wb") as f:
        f.write(img2pdf.convert(images,layout_fun=this_layout))    

    #Remove images
    time.sleep(0.15)
    for image in images:
        os.remove(f"{image}")
    #regenerate images
    convert_pdf_to_png(filepath)
    
    #these_flags = os.O_RDONLY
    #print(f"os.open: {os.open(filepath,flags=these_flags)}")
    #os.open(filepath,flags=these_flags)
    
    try:
        subprocess.call(["xdg-open",filepath]) #linux
    except:
        subprocess.call([filepath],shell=True) #windows
    #Opens the pdf. 
    



    icb_session.console_log(f"Invoice {icb_session.this_invoice['Invoice_ID']} Generated",icb_session.current_console_messages)


    return filepath


def save_invoice_to_database(window,values,filepath):



    
    #Save the invoice to the database
    line_items_str = f"""{icb_session.this_invoice['Line_Items']}""".replace("'",f'"')
    
    invoice_repo = InvoiceRepository(icb_session.connection)
    save_invoice = invoice_repo.insert(
        invoice_id=icb_session.this_invoice['Invoice_ID'],
        customer_id=icb_session.this_invoice['Customer_ID'],
        tracking_code=icb_session.this_invoice['Tracking_Code'],
        line_items=line_items_str,
        due_date=icb_session.this_invoice['Due_Date'][:10],
        created_time=f'{now}',
        edited_time=f'{now}',
        subtotal=icb_session.this_invoice['Subtotal'],
        sales_tax=icb_session.this_invoice['Sales_Tax'],
        total=icb_session.this_invoice['Total'],
        status=icb_session.this_invoice['Status'],
        payment_method='',
        location=filepath
    )

    #Save the transaction 
    
    count_transactions_query = f"""SELECT COUNT(*) FROM {icb_session.ledger_name};"""
    transactions_count = db.execute_read_query_dict(icb_session.connection,count_transactions_query)
    #print(transactions_count)

    this_invoice_subtotal = int(dec(f"{icb_session.this_invoice['Subtotal'].replace(",","")}".replace("$",""))*100)
    accounts_receivable_transaction = int(transactions_count[0]['COUNT(*)'])+1
    add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
    Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction}',
    '15001','{icb_session.transaction_debit_account}', '{this_invoice_subtotal}', 'Invoice {icb_session.this_invoice['Invoice_ID']}', 
    '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
    '{icb_session.this_invoice['Customer_ID']}');"""
    added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
    print(f"added_transaction: {added_transaction}")

    this_invoice_sales_tax = int(dec(f"{icb_session.this_invoice['Sales_Tax'].replace(",","")}".replace("$",""))*100)
    add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
    Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction+1}',
    '13003','{icb_session.transaction_debit_account}', '{this_invoice_sales_tax}', 'Invoice {icb_session.this_invoice['Invoice_ID']} Sales Tax Payable', 
    '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
    '{icb_session.this_invoice['Customer_ID']}');"""
    added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
    print(f"added_transaction: {added_transaction}")
    #write_transaction_query = f"""INSERT INTO {icb_session.ledger_name} ()"""

    return save_invoice







def update_database_properties(window,values):
    icb_session.sales_tax = f"{dec(values[f"-Edit_Sales_Tax-"])/100}"

    database_properties = [
        ["Business Name",f"{f"{values['-edit_db_name-']}".replace("'","''")}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Address",f"{f"{values['-Edit_Business_Address-']}".replace("'","''")}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Owner or Financial Officer Name",f"{values['-Edit_Business_Officer-']}".replace("'","''"),"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Title or Position",f"{values['-Edit_Business_Officer_Title-']}".replace("'","''"),"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Phone Number",f"{values['-Edit_Business_Phone-']}".replace("'","''"),"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Email",f"{f"{values['-Edit_Business_Email-']}".replace("'","''")}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Notes",values[f"-Edit_Business_Notes-"],"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["EIN or SSN",values[f"-Edit_Business_EIN-"],"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Receipts Repository Location",values[f"-Edit_Receipts_Repository-"],"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Sales Tax",icb_session.sales_tax,"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
    ]    
    property_repo = PropertyRepository(icb_session.connection)
    for db_property in database_properties:
        updated_properties = property_repo.update(db_property[0], db_property[1], db_property[3])
        icb_session.console_log(f"Query executed: {updated_properties}",icb_session.current_console_messages)


def update_sku(window,values):

    this_sku = values["-Service_Sku_Input-"]
    this_description = values["-Service_Description_Input-"]
    this_price = values["-Service_Price_Input-"]
    this_taxable = values["-Service_Taxable_Input-"]
    this_long_description = values["-Service_Notes_Display-"]


    sku_repo = SkuRepository(icb_session.connection)
    price_val = int(dec(f"{f'{this_price}'.replace('$','')}".replace(',',''))*100)
    this_updated_sku = sku_repo.update(this_sku, this_description, this_long_description, price_val, this_taxable, icb_session.current_time_display[0])
    icb_session.console_log(this_updated_sku,icb_session.current_console_messages)
    
def update_customer(window,values):
    this_customer = f"{values["-Customer_Number_Display-"]}"[16:]
    this_customer_name = values["-Customer_Name_Input-"]
    this_customer_first = values["-Customer_Contact_First_Input-"]
    this_customer_last = values["-Customer_Contact_Last_Input-"]
    this_customer_preferred = values["-Customer_Contact_Preferred_Input-"]
    this_customer_address = values["-Customer_Address_Input-"]
    this_customer_phone = values["-Customer_Phone_Input-"]
    this_customer_phone_type = values["-Customer_PhoneType_Input-"]
    this_customer_email = values["-Customer_Email_Input-"]
    this_customer_notes = values['-Customer_Notes_Display-']

    update_customer_query = f"""UPDATE tbl_Customers SET Edited_Time = '{icb_session.current_time_display[0]}', Customer_Company_Name = "{this_customer_name}", Customer_First_Name = "{this_customer_first}", Customer_Last_Name = "{this_customer_last}", Preferred_Name = "{this_customer_preferred}", Customer_Phone_Number = "{this_customer_phone}", Customer_Phone_Number_Type = '{this_customer_phone_type}', Customer_Address = "{this_customer_address}", Customer_Email = '{this_customer_email}', Notes = "{this_customer_notes}" WHERE Customer_ID = {this_customer};"""
    this_updated_customer = db.execute_query(icb_session.connection,update_customer_query)
    icb_session.console_log(this_updated_customer,icb_session.current_console_messages)    


def update_vendor(window,values):
    this_vendor = f"{values["-Vendor_Number_Display-"]}"[14:]
    this_vendor_name = values["-Vendor_Name_Input-"]
    this_vendor_category = values["-Vendor_Category_Input-"]
    this_vendor_first = values["-Vendor_Contact_First_Input-"]
    this_vendor_last = values["-Vendor_Contact_Last_Input-"]
    this_vendor_preferred = values["-Vendor_Contact_Preferred_Input-"]
    this_vendor_address = values["-Vendor_Address_Input-"]
    this_vendor_phone = values["-Vendor_Phone_Input-"]
    this_vendor_phone_type = values["-Vendor_PhoneType_Input-"]
    this_vendor_email = values["-Vendor_Email_Input-"]
    this_vendor_website = values['-Vendor_Website_Input-']
    this_vendor_notes = values['-Vendor_Notes_Display-']

    vendor_repo = VendorRepository(icb_session.connection)
    this_updated_vendor = vendor_repo.update(this_vendor, this_vendor_name, this_vendor_category, this_vendor_first, this_vendor_last, this_vendor_preferred, this_vendor_phone, this_vendor_phone_type, this_vendor_address, this_vendor_email, this_vendor_website, this_vendor_notes, icb_session.current_time_display[0])
    icb_session.console_log(this_updated_vendor,icb_session.current_console_messages)    



#------------------------------------------Section 6 Window and Event Loop
#░▒▓████████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓████████▓▒░ ░▒▓███████▓▒░  ░▒▓████████▓▒░       ░▒▓█▓▒░         ░▒▓██████▓▒░   ░▒▓██████▓▒░  ░▒▓███████▓▒░  
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░           ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ 
#░▒▓█▓▒░         ░▒▓█▓▒▒▓█▓▒░  ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░           ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ 
#░▒▓██████▓▒░    ░▒▓█▓▒▒▓█▓▒░  ░▒▓██████▓▒░   ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░           ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓███████▓▒░  
#░▒▓█▓▒░          ░▒▓█▓▓█▓▒░   ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░           ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        
#░▒▓█▓▒░          ░▒▓█▓▓█▓▒░   ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░           ░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░        
#░▒▓████████▓▒░    ░▒▓██▓▒░    ░▒▓████████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░           ░▒▓████████▓▒░  ░▒▓██████▓▒░   ░▒▓██████▓▒░  ░▒▓█▓▒░        
                                                                                                                                        
icb_session.window = sg.Window(title="Iceberg Accounting Suite", layout= layout1, margins=(10,10), resizable=True, size=(1280,980), finalize=True)
event, values = icb_session.window.read(10)
icb_session.console_log(f"""{icb_session.current_console_messages[0]}""",[])


icb_session.current_time_display = get_current_time_info()

while True:
    #window_read = window.read()
    #print(window_read)
    if event == "Exit Iceberg" or event == sg.WIN_CLOSED:

        if icb_session.save_location == None or icb_session.save_location== "" or icb_session.save_location == ".":
            icb_session.save_location = "./"
        if icb_session.save_location[-1] != "/":
            icb_session.save_location = icb_session.save_location + "/"
        db.save_database(icb_session.session_log_connection,"sessions.icbs","sessions.icbskey",False)
        break
    event, values = icb_session.window.read(timeout=990)
    if event == '__TIMEOUT__':
        #Synchronizes the time
        if icb_session.guitimer == "Initializing": 
            
            print("Initializing: " + icb_session.current_time_display[0])
            #print(icb_session.current_time_display[1][-6:-4])
            icb_session.guitimer = int(icb_session.current_time_display[1][-6:-4])

        elif icb_session.guitimer >57 or icb_session.guitimer == 0:

                icb_session.synchronized = synchronize_time(icb_session.window, icb_session.current_time_display)
                if icb_session.synchronized[0] == "No":
                    #print(f"""Synchronizing: {timer}""")
                    icb_session.guitimer = int(icb_session.synchronized[1][1][-6:-4])
                else:
                    icb_session.current_time_display = icb_session.synchronized[1]
                    icb_session.guitimer = int(icb_session.current_time_display[1][-6:-4])
                    icb_session.window['-Current_Time_Display-'].update(icb_session.current_time_display[0])
                    #print(f"""Synchronized: {icb_session.current_time_display[0]}""")
                    #print(f"""{timer}""")

                    if (int("1" + icb_session.current_time_display[1][-9:-7]))%5 == 0 and icb_session.database_loaded:

                        if icb_session.save_location == None or icb_session.save_location== "" or icb_session.save_location == ".":
                            icb_session.save_location = "./"
                        if icb_session.save_location[-1] != "/":
                            icb_session.save_location = icb_session.save_location + "/"
                        message, icb_session.connection = db.save_database(icb_session.connection, icb_session.db_name, icb_session.filename, icb_session.save_location)
                        #update_dashboard_statistics(icb_session.connection, window, ledger_name, icb_session.db_name, values)
                        icb_session.console_log(message,icb_session.current_console_messages)

                    if icb_session.guitimer > 0:
                        conditional_s = "s"
                        if icb_session.guitimer == 1:
                            conditional_s = ""
                        icb_session.current_console_messages = icb_session.console_log(f"""Minute update delayed by {icb_session.guitimer} second{conditional_s}.""", icb_session.current_console_messages)
        else:
            current_time = get_current_time_info()
            icb_session.guitimer = int(current_time[1][-6:-4])
            #print(timer)


        #todo: Autosave
        #todo: Update employee timekeeping when active
        #icb_session.window['-Current_Time_Display-'].update(f"""{datetime.datetime.now().month}/{datetime.datetime.now().day}/{datetime.datetime.now().year}  -  {datetime.datetime.now().hour}:{format(datetime.datetime.now().minute,'02d')}""")
    #else:
        #print(f"""Time Counter Counting {time_counter}""")
        #time_counter = time_counter + 1
    else:
        function_triggered = True
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        #elif event == "-Create_Database-":
        #    icb_session.filekey,icb_session.filename, icb_session.ledger_name = create_database(values, connection, current_console_messages,icb_session.window)
        #    current_console_messages = console_log(icb_session.window, f"""Filekey: {filekey}, filename: {filename}""",connection,current_console_messages)
        elif event == "Go to Dashboard":
            this_tab_index = 0
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            update_dashboard_statistics(icb_session.window, values)
        elif event == "-Account_Type_Picker-" or event == "-Account_Year_Picker-":
            #print("Account Type Picker")
            
            if icb_session.connection:
                if values["-Account_Type_Picker-"] == "All Accounts":
                    update_chart_of_accounts(icb_session.window, values, "Al", f"{values['-Account_Year_Picker-']}")
                else:
                    update_chart_of_accounts(icb_session.window, values, values["-Account_Type_Picker-"][:2], f"{values['-Account_Year_Picker-']}")

            
        elif event == "View Ledger" or event == "Search Transactions" or event == "New Transaction" or event == "-New_Transaction_Button-":
            this_tab_index = 1
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            load_ledger_tab(icb_session.window, values)
            if event=="New Transaction" or event == "-New_Transaction_Button-":
                this_layout, icb_session.num = new_transaction_layout(icb_session.num)
                #print(this_layout, icb_session.num)
                #print("this_layout")
                new_transaction_window = sg.Window(title="Record a New Transaction", location=(700,200),layout= this_layout, margins=(10,2), resizable=True, size=(920,460))
                new_transaction_window.close_destroys_window = True

                #TODO: Figure out how to update a popup window to remove an account from the list of accounts. 
                # This way an account selected as a credit will not appear in the list of possible debit accounts.
                #revised_accounts = remove_account_in_use(icb_session.window, values, event_newt)
                #if event_newt == f"-Transaction_Debit_Account_{icb_session.num}-":
                #    icb_session.window[f'-Transaction_Credit_Account_{icb_session.num}-'].update(revised_accounts)
                #if event_newt == f"-Transaction_Credit_Account_{icb_session.num}-":
                #    icb_session.window[f'-Transaction_Debit_Account_{icb_session.num}-'].update(revised_accounts)
                transaction_date = icb_session.current_date
                check = False
                #print("while loop starting")
                while True:
                    event_newt, values_newt = new_transaction_window.read(close=False)
                    #print(event_newt)
                    if check:
                        check = False
                        icb_session.current_console_messages = icb_session.console_log(f"{event_newt}",icb_session.current_console_messages)
                    if values_newt != None:
                        values.update(values_newt)
                    if event_newt == sg.WIN_CLOSED:
                        break
                    elif event_newt == f"-Transaction_Date_{icb_session.num}-": 
                        icb_session.transaction_date = values[f'-Transaction_Date_String_{icb_session.num}-']
                        #this_transaction_date = icb_session.transaction_date
                        #icb_session.transaction_date = datetime.datetime(this_transaction_date[2],this_transaction_date[0],this_transaction_date[1])
                        #print("icb_session.transaction_date")
                        #print(icb_session.transaction_date)
                        #new_transaction_window[f"-Transaction_Date_{icb_session.num}-"].update(icb_session.transaction_date)


                    elif event_newt == f"-Transaction_Image_Input_{icb_session.num}-":
                        image_url = values[f'-Transaction_Image_Input_{icb_session.num}-']
                        if image_url[-4:] == ".pdf" :
                            image_from_path = convert_pdf_to_png(image_url)
                            if image_from_path != "Error: File is not a pdf":
                                new_transaction_window[f"-Transaction_Image_Display_{icb_session.num}-"].update(image_from_path[0], subsample=1)
                        elif image_url[-4:] == ".jpg" or image_url[-4:] == ".jpeg" or image_url[-4:] == ".png" or image_url[-4:] == ".ppm" or image_url[-4:] == ".tiff" or image_url[-4:] == ".bmp" or image_url[-4:] == ".gif":
                            this_image = Image.open(image_url)
                            num_subsamples = int((this_image.height/360+this_image.width/350)/2)+1
                            new_transaction_window[f"-Transaction_Image_Display_{icb_session.num}-"].update(image_url, subsample=num_subsamples)


                    elif event_newt == f"-Submit_Transaction_Button_{icb_session.num}-":
                        if new_transaction_window[f"-Submit_Transaction_Button_{icb_session.num}-"].ButtonText == "Submit" and values_newt[f"-Transaction_Name_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Date_String_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Amount_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Debit_Account_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Credit_Account_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Debit_Account_{icb_session.num}-"] != values_newt[f"-Transaction_Credit_Account_{icb_session.num}-"]:
                            new_transaction_window[f"-Submit_Transaction_Button_{icb_session.num}-"].update("Really?")
                        elif new_transaction_window[f"-Submit_Transaction_Button_{icb_session.num}-"].ButtonText == "Really?" and values_newt[f"-Transaction_Name_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Date_String_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Amount_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Debit_Account_{icb_session.num}-"] != "" and values_newt[f"-Transaction_Credit_Account_{icb_session.num}-"] != "":

                            add_transaction_to_database(values)
                            icb_session.transaction = load_ledger_tab(icb_session.window,values)
                            new_transaction_window.close()

                #new_transaction_window.close()
        elif event == "Open Database":    
            
            this_layout, icb_session.num = open_database_layout(icb_session.num)
            #print(this_layout, icb_session.num)
            new_database_window = sg.Window(title="Open a Database", location=(900,500),layout= this_layout, margins=(10,10), resizable=True, size=(480,120))
            event_opendb, values_opendb = new_database_window.read(close=True)
            values.update(values_opendb)
            if event_opendb == f"-Open_Database_Button_{icb_session.num}-": 
                icb_session.connection = False
                fileloc = str(values[f"-Open_File_{icb_session.num}-"])
                db_name_0 = fileloc[:-3]
                icb_session.filekey=""
                filename_0 = fileloc
                
                
                remove_to = filename_0[::-1].index("/")
                #print("1042")
                icb_session.filename = filename_0[-remove_to:]

                #print(f"1053 filename: {icb_session.filename}")


                remove_to = db_name_0[::-1].index("/")
                #print("1042")
                icb_session.db_name = db_name_0[-remove_to:]
                #icb_session.ledger_name = f"tbl_ledger_{icb_session.db_name[:-4]}_CY{values['-Year_Picker-']}" #Comment out the year picker
                #print(icb_session.db_name)

                icb_session.database_loaded = True
                icb_session.save_location = db_name_0[:-remove_to]
                if icb_session.save_location == None or icb_session.save_location== "" or icb_session.save_location == ".":
                    icb_session.save_location = "./"
                if icb_session.save_location[-1] != "/":
                    icb_session.save_location = icb_session.save_location + "/"
                #print(f"1044 {icb_session.filekey} {icb_session.db_name}; {icb_session.save_location}")
                with open(f"{icb_session.save_location}{icb_session.filename}",'rb') as file:
                    icb_session.filekey = file.read()
                #print(f"1049 filekey: {icb_session.filekey}; db_name: {icb_session.db_name}; save_location: {icb_session.save_location}")
                icb_session.connection, icb_session.filekey = db.open_database(icb_session.filename, icb_session.db_name, icb_session.save_location)
                
                #Load the database properties
                property_repo = PropertyRepository(icb_session.connection)
                icb_session.ledger_name = property_repo.get('Ledger Name') or ""
                #Log to console
                icb_session.current_console_messages = icb_session.console_log(f"Filekey Read: {icb_session.filename}", icb_session.current_console_messages)
                icb_session.current_console_messages = icb_session.console_log(f"Database Opened: {icb_session.db_name}", icb_session.current_console_messages)
                icb_session.current_console_messages = icb_session.console_log("Dashboard statistics updated.", icb_session.current_console_messages)

                #Load the database properties

                icb_session.business_name = property_repo.get('Business Name') or ""
                icb_session.business_address = property_repo.get('Address') or ""
                icb_session.owner_name = property_repo.get('Owner or Financial Officer Name') or ""
                icb_session.owner_title = property_repo.get('Title or Position') or ""
                icb_session.owner_phone = property_repo.get('Phone Number') or ""
                icb_session.owner_email = property_repo.get('Email') or ""
                icb_session.owner_notes = property_repo.get('Notes') or ""
                icb_session.business_ein = property_repo.get('EIN or SSN') or ""
                
                sales_tax_value = property_repo.get('Sales Tax')
                if sales_tax_value:
                    icb_session.sales_tax = dec(sales_tax_value)



                #Switch to the dashboard and update statistics
                this_tab_index = 0
                for i in range(len(tab_keys)):
                    if i == this_tab_index:
                        icb_session.window[tab_keys[i]].update(visible=True)
                        icb_session.window[tab_keys[i]].select()
                    else:
                        icb_session.window[tab_keys[i]].update(visible=False)                
                
                
                
                icb_session.window, chart_of_accounts_display_content = update_dashboard_statistics(icb_session.window, values)
                #print(menu_def[0][1])
                icb_session.window['-Program_Menu-'].update(menu_def_2)

            #print(values)
        elif event == "-Ledger_Display_Content-":
            ledger_content = values['-Ledger_Display_Content-']
            #print(ledger_content)
            if len(ledger_content) != 0:
                this_transaction_index = ledger_content[0]
                this_transaction = icb_session.transactions[this_transaction_index][0]
                load_transaction_details(this_transaction)
        elif event == "-Ledger_Search_Input-" or event == "-Ledger_Year_Picker-":
            #print(values["-Ledger_Search_Input-"])
            search_ledger(icb_session.window,values)
        elif event == "-Save_Revised_Properties-":
            update_database_properties(icb_session.window,values)
        elif event == "Profit and Loss":
            this_tab_index = 2
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            
        elif event == "View Vendors" or event=="New Vendor" or event == f"-New_Vendor_Button-":
            this_tab_index = 3
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            if event == "View Vendors" or event=="New Vendor":
                load_vendors_tab(icb_session.window,values)
            if event=="New Vendor" or event == f"-New_Vendor_Button-":
                vendor_repo = VendorRepository(icb_session.connection)
                max_id = vendor_repo.get_max_id()
                new_vendor_number = [(max_id,)]
                #print(icb_session.vendor_number)
                #print(new_vendor_number[0][0])
                if type(new_vendor_number[0][0]) !=int:
                    icb_session.vendor_number = int(1)
                else:
                    icb_session.vendor_number = new_vendor_number[0][0] + 1
                this_layout, icb_session.num = new_vendor_layout(icb_session.num,icb_session.vendor_number)
                #print(this_layout, icb_session.num)
                new_vendor_window = sg.Window(title="Add a Vendor", location=(900,200),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
                new_vendor_window.close_destroys_window = True
                while True:
                    event_newv, values_newv = new_vendor_window.read(close=False)
                    #values.update(values_newv)  
                    if event_newv == sg.WIN_CLOSED:
                        break      
                    if event_newv == f"-Submit_Vendor_Button_{icb_session.num}-" and values_newv[f"-Vendor_Name_{icb_session.num}-"] != "":
                        print(f"""Adding {values_newv[f'-Vendor_Name_{icb_session.num}-']}""")
                        add_vendor_to_database(icb_session.window,values_newv)
                        load_vendors_tab(icb_session.window,values)
                        new_vendor_window.close()
        elif event=="-View_Vendors_Content-":
            #print(event)
            this_index = values["-View_Vendors_Content-"]     
            #print(this_index)
            if len(this_index) > 0:
                load_single_vendor(icb_session.window, values, icb_session.vendors[this_index[0]])          
        elif event == "View Customers" or event == "New Customer" or event == f"-New_Customer_Button-":
            this_tab_index = 4
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            update_customers_view(icb_session.window,values)
            if event == "New Customer" or event == f"-New_Customer_Button-":
                customer_number_query = f"""SELECT MAX(Customer_ID) FROM tbl_Customers;"""
                new_customer_number = db.execute_read_query(icb_session.connection,customer_number_query)
                #print(icb_session.customer_number)
                #print(new_customer_number[0][0])
                
                if type(new_customer_number[0][0]) != int:
                    icb_session.customer_number = int(1)
                else:
                    icb_session.customer_number = new_customer_number[0][0] + 1
                this_layout, icb_session.num = new_customer_layout(icb_session.num,icb_session.customer_number)
                #print(this_layout, icb_session.num)
                new_customer_window = sg.Window(title="Add a Customer", location=(900,200),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
                new_customer_window.close_destroys_window = True
                while True:
                    event_newc, values_newc = new_customer_window.read(close=False)
                    #values.extend(values_newc)    ]
                    if event_newc == sg.WIN_CLOSED:
                        break  
                    elif event_newc == f"-Submit_Customer_Button_{icb_session.num}-" and values_newc[f"-Customer_Address_{icb_session.num}-"] != '':
                        print(f"""Adding {values_newc[f'-Customer_Name_{icb_session.num}-']}""")
                        add_customer_to_database(icb_session.window,values_newc)    
                        #print("Added customer")
                        update_customers_view(icb_session.window,values)
                        new_customer_window.close()
        elif event == "-Customers_Search_Input-":
            update_customers_view(icb_session.window,values)    
#        elif event == "-New_Customer_Button-":
#                customer_number_query = f"""SELECT MAX(Customer_ID) FROM tbl_Customers;"""
#                new_customer_number = db.execute_read_query(icb_session.connection,customer_number_query)
#                #print(icb_session.customer_number)
#                #print(new_customer_number[0][0])
#                
#                if type(new_customer_number[0][0]) != int:
#                    icb_session.customer_number = int(0)
#                else:
#                    icb_session.customer_number = new_customer_number[0][0] + 1
#                this_layout, icb_session.num = new_customer_layout(icb_session.num,icb_session.customer_number)
#                #print(this_layout, icb_session.num)
#                new_customer_window = sg.Window(title="Add a Customer", location=(900,200),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
#                new_customer_window.close_destroys_window = True
#                event_newc, values_newc = new_customer_window.read(close=True)
#                values.update(values_newc)      
#                if event_newc == f"-Submit_Customer_Button_{icb_session.num}-":
#                    print(f"""Adding {values[f'-Customer_Name_{icb_session.num}-']}""")
#                    add_customer_to_database(icb_session.window,values)    
#                    print("Added customer")
#                    update_customers_view(icb_session.window,values)       
        elif event=="-View_Customers_Content-":
            #print(event)
            this_index = values["-View_Customers_Content-"]     
            #print(this_index)
            if len(this_index) > 0:
                load_single_customer(icb_session.window, values, icb_session.customers[this_index[0]])   
        elif event == "Point of Sale":
            this_tab_index = 5
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            update_pos_view(icb_session.window,values)
        elif event == "-POS_Search_Input-":
            update_pos_view(icb_session.window,values)
        elif event == "View Inventory":
            this_tab_index = 6
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
        elif event == "Equity Dashboard":
            this_tab_index = 7
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
        elif event == "New Database":
            
            this_layout, icb_session.num = new_database_layout(icb_session.num)
            #print(this_layout, icb_session.num)
            new_database_window = sg.Window(title="Create a New Database", location=(900,500),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
            new_database_window.close_destroys_window = True
            while True:
                event_newdb, values_newdb = new_database_window.read(close=False)
                if values_newdb:
                    values.update(values_newdb)
                if event_newdb == sg.WIN_CLOSED:
                    break
                elif event_newdb == f"-Submit_New_Database_Button_{icb_session.num}-" and values_newdb[f"-db_name_{icb_session.num}-"] != "" and values_newdb[f"-Business_Address_{icb_session.num}-"] != "" and values_newdb[f"-Save_Location_{icb_session.num}-"] != "" and values_newdb[f"-Business_Receipts_Repository_{icb_session.num}-"] != "" and values_newdb[f'-Business_SalesTax_{icb_session.num}-'] != "": 
                    icb_session.connection = False
                    icb_session.filekey, icb_session.filename,  chart_of_accounts_display_content = create_database(values, icb_session.current_console_messages, icb_session.window, icb_session.num, current_year)
                    #print(ledger_name)
                    if icb_session.filename:
                        icb_session.current_console_messages = icb_session.console_log(f"Database created: {icb_session.db_name}", icb_session.current_console_messages)
                        icb_session.current_console_messages = icb_session.console_log(f"Filekey created: {icb_session.filename}", icb_session.current_console_messages)
                        icb_session.current_console_messages = icb_session.console_log("Dashboard statistics updated.", icb_session.current_console_messages)
                        icb_session.guitimer = "Initializing"
                        #Test to toggle menu items enabled/disabled
                        #print(menu_def[0][1])
                        #menu_def[0][1][3] = "Save Database &As"


                        #print(menu_def[0][1])
                        icb_session.window['-Program_Menu-'].update(menu_def_2)
                        new_database_window.close()
        #elif event == "-Year_Picker-": 
        #    icb_session.window, chart_of_accounts_display_content = update_dashboard_statistics(icb_session.window, values)

        elif event == "Save Database":    
                if icb_session.save_location == None or icb_session.save_location== "" or icb_session.save_location == ".":
                    icb_session.save_location = "./"
                if icb_session.save_location[-1] != "/":
                    icb_session.save_location = icb_session.save_location + "/"
                message, icb_session.connection = db.save_database(icb_session.connection, icb_session.db_name, icb_session.filename, icb_session.save_location)
                #update_dashboard_statistics(icb_session.connection, window, ledger_name, icb_session.db_name, values)
                icb_session.current_console_messages = icb_session.console_log(message, icb_session.current_console_messages)
                #current_console_messages = console_log(window, "Dashboard statistics updated.", current_console_messages)
        elif event == "-Transaction_Image_Button-":
            try:
                subprocess.call(["xdg-open",f"{icb_session.window["-Transaction_Image_Button-"].ButtonText}"]) #linux
            except:
                subprocess.call([icb_session.window["-Transaction_Image_Button-"].ButtonText],shell=True) #windows
        elif event == "-Edit_Transaction_Button-":
            activate_edit_transaction_fields(icb_session.window,values)    
        elif event == "-View_Account_Button-":# or event == "-Chart_of_Accounts_Content-":
            if icb_session.connection:
                account_index = values["-Chart_of_Accounts_Content-"]
                #print(account_index[0])
                window, chart_of_accounts_display_content = update_dashboard_statistics(icb_session.window, values)
                #print(chart_of_accounts_display_content)
                try:
                    account_number = chart_of_accounts_display_content[account_index[0]][0]
                    this_tab_index = 8
                    for i in range(len(tab_keys)):
                        if i == this_tab_index:
                            icb_session.window[tab_keys[i]].update(visible=True)
                            icb_session.window[tab_keys[i]].select()
                        else:
                            icb_session.window[tab_keys[i]].update(visible=False)
                    icb_session.window, values = load_view_account_tab(icb_session.window, values, account_number, icb_session.ledger_name)
                except:
                    pass

        elif event == "Database Properties":
            this_tab_index = 9
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            load_database_properties_tab(icb_session.window, values, icb_session.connection)
        elif event == "-Edit_Vendor_Button-":
            if icb_session.window["-Edit_Vendor_Button-"].ButtonText == "Edit Vendor" and values['-Vendor_Name_Input-'] != '':
                icb_session.window["-Edit_Vendor_Button-"].update("Save Vendor")
                icb_session.window["-Vendor_Name_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Category_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Contact_First_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Contact_Last_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Contact_Preferred_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Address_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Phone_Input-"].update(disabled=False)
                icb_session.window["-Vendor_PhoneType_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Email_Input-"].update(disabled=False)
                icb_session.window["-Vendor_Website_Input-"].update(disabled=False)
                icb_session.window['-Vendor_Notes_Display-'].update(disabled=False)

            elif icb_session.window["-Edit_Vendor_Button-"].ButtonText == "Save Vendor" and values['-Vendor_Name_Input-'] != '':
                icb_session.window["-Edit_Vendor_Button-"].update("Edit Vendor")
                icb_session.window["-Vendor_Name_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Category_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Contact_First_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Contact_Last_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Contact_Preferred_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Address_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Phone_Input-"].update(disabled=True)
                icb_session.window["-Vendor_PhoneType_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Email_Input-"].update(disabled=True)
                icb_session.window["-Vendor_Website_Input-"].update(disabled=True)
                icb_session.window['-Vendor_Notes_Display-'].update(disabled=True)
                update_vendor(icb_session.window,values)
                load_vendors_tab(icb_session.window, values) 
        elif event == "-Vendors_Search_Input-":
            load_vendors_tab(icb_session.window, values) 
        elif event == "-Edit_Customer_Button-":
            if icb_session.window["-Edit_Customer_Button-"].ButtonText == "Edit Customer" and values['-Customer_Address_Input-'] != '':
                icb_session.window["-Edit_Customer_Button-"].update("Save Customer")
                icb_session.window["-Customer_Name_Input-"].update(disabled=False)
                icb_session.window["-Customer_Contact_First_Input-"].update(disabled=False)
                icb_session.window["-Customer_Contact_Last_Input-"].update(disabled=False)
                icb_session.window["-Customer_Contact_Preferred_Input-"].update(disabled=False)
                icb_session.window["-Customer_Address_Input-"].update(disabled=False)
                icb_session.window["-Customer_Phone_Input-"].update(disabled=False)
                icb_session.window["-Customer_PhoneType_Input-"].update(disabled=False)
                icb_session.window["-Customer_Email_Input-"].update(disabled=False)
                icb_session.window["-Customer_Notes_Display-"].update(disabled=False)

            elif icb_session.window["-Edit_Customer_Button-"].ButtonText == "Save Customer":
                icb_session.window["-Edit_Customer_Button-"].update("Edit Customer")
                icb_session.window["-Customer_Name_Input-"].update(disabled=True)
                icb_session.window["-Customer_Contact_First_Input-"].update(disabled=True)
                icb_session.window["-Customer_Contact_Last_Input-"].update(disabled=True)
                icb_session.window["-Customer_Contact_Preferred_Input-"].update(disabled=True)
                icb_session.window["-Customer_Address_Input-"].update(disabled=True)
                icb_session.window["-Customer_Phone_Input-"].update(disabled=True)
                icb_session.window["-Customer_PhoneType_Input-"].update(disabled=True)
                icb_session.window["-Customer_Email_Input-"].update(disabled=True)
                icb_session.window["-Customer_Notes_Display-"].update(disabled=True)
                update_customer(icb_session.window,values)
                update_customers_view(icb_session.window, values) 




        elif event == "-Edit_Service_Button-":
            if icb_session.window["-Edit_Service_Button-"].ButtonText == "Edit SKU" and values['-Service_Sku_Input-'] != '':
                icb_session.window["-Edit_Service_Button-"].update("Save SKU")
                #icb_session.window["-Service_Sku_Input-"].update(disabled=False)
                icb_session.window["-Service_Description_Input-"].update(disabled=False)
                icb_session.window["-Service_Price_Input-"].update(disabled=False)
                icb_session.window["-Service_Taxable_Input-"].update(disabled=False)
                icb_session.window["-Service_Notes_Display-"].update(disabled=False)

            elif icb_session.window["-Edit_Service_Button-"].ButtonText == "Save SKU" and values['-Service_Sku_Input-'] != '':
                icb_session.window["-Edit_Service_Button-"].update("Edit SKU")
                #icb_session.window["-Service_Sku_Input-"].update(disabled=True)
                icb_session.window["-Service_Description_Input-"].update(disabled=True)
                icb_session.window["-Service_Price_Input-"].update(disabled=True)
                icb_session.window["-Service_Taxable_Input-"].update(disabled=True)
                icb_session.window["-Service_Notes_Display-"].update(disabled=True)
                update_sku(icb_session.window,values)
                load_services_tab(icb_session.window, values) 
        elif event == "Documentation":
            try:
                subprocess.call(["xdg-open","./readme.pdf"]) #linux
            except:
                subprocess.call(["readme.pdf"],shell=True) #windows
        elif event == "About":
            this_tab_index = 11
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)            
        elif event == "View Services" or event == "New Service" or event == "-New_Service_Button-" or event == '-Services_Search_Input-':
            this_tab_index = 10
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            load_services_tab(icb_session.window, values)   
            if event == "New Service" or event == "-New_Service_Button-":
                sku_repo = SkuRepository(icb_session.connection)
                max_sku = sku_repo.get_max_sku()
                new_service_number = [(max_sku,)]
                print(f"New service {new_service_number[0][0]}")
                #print(new_customer_number[0][0])
                
                if type(new_service_number[0][0]) != str:
                    icb_session.service_number = int(10001)
                else:
                    icb_session.service_number = int(new_service_number[0][0]) + 1
                this_layout, icb_session.num = new_service_layout(icb_session.num,icb_session.service_number)
                #print(this_layout, icb_session.num)
                new_service_window = sg.Window(title="Add a Service", location=(900,200),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
                new_service_window.close_destroys_window = True
                while True:
                    event_news, values_news = new_service_window.read(close=False)
                    #values.extend(values_news)      
                    if event_news == sg.WIN_CLOSED:
                        break
                    elif event_news == f"-Submit_Service_Button_{icb_session.num}-" and values_news[f"-Service_Description_{icb_session.num}-"] != "" and values_news[f"-Service_Price_{icb_session.num}-"] and values_news[f"-Service_Taxable_{icb_session.num}-"] != "":
                        print(f"""Adding {values_news[f'-Service_Description_{icb_session.num}-']}""")
                        add_service_to_database(icb_session.window,values_news)    
                        #print("Added customer")
                        load_services_tab(icb_session.window,values) 
                        new_service_window.close()
        elif event == "-View_Services_Content-" :
            #print(event)
            this_index = values["-View_Services_Content-"]     
            #print(this_index)
            if len(this_index) > 0:
                load_single_service(icb_session.window,values, icb_session.services[this_index[0]])    

     
        elif event == "-Edit_Account_Button-":
            #print(values['-Edit_Account_Button-'])
            if icb_session.window['-Edit_Account_Button-'].ButtonText == "Edit Account":
                icb_session.window['-Edit_Account_Button-'].update("Save Changes")
                icb_session.window['-Edit_Account_Name_Input-'].update(disabled=False)
                icb_session.window['-Edit_Account_Bank-'].update(disabled=False)
                icb_session.window['-Edit_Account_Bank_Acct_Routing-'].update(disabled=False)
                icb_session.window['-Edit_Account_Bank_Acct_Number-'].update(disabled=False)
                icb_session.window['-Edit_Account_Bank_Acct_Type-'].update(disabled=False)
                icb_session.window['-Account_Notes_Display-'].update(disabled=False, background_color="white")
            elif icb_session.window['-Edit_Account_Button-'].ButtonText == "Save Changes":
                icb_session.window['-Edit_Account_Button-'].update("Edit Account")
                icb_session.window['-Edit_Account_Name_Input-'].update(disabled=True)
                icb_session.window['-Edit_Account_Bank-'].update(disabled=True)
                icb_session.window['-Edit_Account_Bank_Acct_Routing-'].update(disabled=True)
                icb_session.window['-Edit_Account_Bank_Acct_Number-'].update(disabled=True)
                icb_session.window['-Edit_Account_Bank_Acct_Type-'].update(disabled=True)
                icb_session.window['-Account_Notes_Display-'].update(disabled=True, background_color=detailed_information_color)
                save_account_changes(icb_session.window, values)
                icb_session.current_console_messages = icb_session.console_log(db.save_database(icb_session.connection,icb_session.db_name,icb_session.filename,icb_session.save_location),icb_session.current_console_messages)
        elif event == "-New_Account_Button-":
            if icb_session.connection:
                this_layout, icb_session.num = new_account_layout(icb_session.num)
                new_account_window = sg.Window(title="Add an Account", location=(900,500),layout= this_layout, margins=(10,10), resizable=True, size=(480,600))
                
                while True:
                    event_newacc, values_newacc = new_account_window.read(close=False)
                    if values_newacc != None:
                        values.update(values_newacc)
                    if event_newacc == sg.WIN_CLOSED:
                        break
                    elif event_newacc == f"-Account_Type_Picker_{icb_session.num}-":
                        pass
                    elif event_newacc == f"-Submit_Account_Button_{icb_session.num}-" and values_newacc[f"-Account_Name_{icb_session.num}-"] != "":        
                        added_account = add_account_to_database(values)     
                        icb_session.current_console_messages = icb_session.console_log(f"New Account Created: {added_account}",icb_session.current_console_messages)
                        new_account_window.close()
                        update_dashboard_statistics(icb_session.window,values)
        elif event == f"-New_Invoice_Button-":

            invoice_layout, icb_session.num = new_invoice_layout(icb_session.num)
            #print(this_layout, icb_session.num)
            #print("this_layout")
            #print(invoice_layout)
            invoice_repo = InvoiceRepository(icb_session.connection)
            this_invoice_id = int(invoice_repo.get_count()) + 10001
            #print(f"{this_invoice_id}")
            new_invoice_window = sg.Window(title=f"Record Invoice {this_invoice_id}", location=(700,200),layout= invoice_layout, margins=(10,2), resizable=True, size=(750,400))
            new_invoice_window.close_destroys_window = True

            invoice_date = icb_session.current_date
            check = False
            icb_session.these_line_items = []
            #print("while loop starting")
            while True:
                event_newi, values_newi = new_invoice_window.read(close=False)
                #print(event_newt)
                this_customer = ""
                if check:
                    check = False
                    icb_session.current_console_messages = icb_session.console_log(f"{event_newi}",icb_session.current_console_messages)
                if values_newi != None:
                    values.update(values_newi)
                if event_newi == sg.WIN_CLOSED:
                    break
                elif event_newi == f"-Invoice_Customer_Search_{icb_session.num}-": 
                    search_term = values_newi[f"-Invoice_Customer_Search_{icb_session.num}-"]
                    customer_search_query = f"""SELECT Customer_ID, Customer_Company_Name, Customer_First_Name, Customer_Last_Name FROM tbl_Customers WHERE Customer_First_Name LIKE '%{search_term}%' OR Customer_Last_Name LIKE '%{search_term}%' OR Customer_Company_Name LIKE '%{search_term}%' OR Preferred_Name LIKE '%{search_term}%' OR Customer_Phone_Number LIKE '%{search_term}%' OR Customer_Email LIKE '%{search_term}%' OR Notes LIKE '%{search_term}%';"""
                    customers = db.execute_read_query_dict(icb_session.connection,customer_search_query)
                    #new_transaction_window[f"-Transaction_Date_{icb_session.num}-"].update(icb_session.transaction_date)
                    icb_session.these_customers = []
                    for customer in customers:
                        icb_session.these_customers.append([f"{customer['Customer_ID']}",f"{customer['Customer_Company_Name']}",f"{customer['Customer_First_Name']}",f"{customer['Customer_Last_Name']}"])
                    new_invoice_window[f'-Invoice_Customers_Results_{icb_session.num}-'].update(icb_session.these_customers)
                elif event_newi == f'-Invoice_Customers_Results_{icb_session.num}-':
                    #print(values_newi[f'-Invoice_Customers_Results_{icb_session.num}-'])
                    
                    if len(values_newi[f'-Invoice_Customers_Results_{icb_session.num}-']) > 0:
                        this_customer = int(icb_session.these_customers[values_newi[f'-Invoice_Customers_Results_{icb_session.num}-'][0]][0])
                    #print(this_customer)
                    icb_session.this_invoice["Customer_ID"] = this_customer
                    get_customer_query = f"""SELECT * from tbl_Customers WHERE Customer_ID ={this_customer};"""
                    this_customer_complete = db.execute_read_query_dict(icb_session.connection,get_customer_query)
                    #print(this_customer_complete)
                    if type(this_customer_complete) != str:
                        new_invoice_window[f"-Invoice_Customer_Name_{icb_session.num}-"].update(this_customer_complete[0]['Customer_Company_Name'])
                        new_invoice_window[f"-Invoice_Customer_Address_{icb_session.num}-"].update(this_customer_complete[0]['Customer_Address'])
                        new_invoice_window[f"-Invoice_Customer_Contact_{icb_session.num}-"].update(f"{this_customer_complete[0]['Customer_First_Name']} {this_customer_complete[0]['Customer_Last_Name']}")
                elif event_newi == f"-Invoice_Search_Input_{icb_session.num}-":

                    search_term = values_newi[f"-Invoice_Search_Input_{icb_session.num}-"]
                    sku_repo = SkuRepository(icb_session.connection)
                    skus = sku_repo.search(search_term)
                    #new_transaction_window[f"-Transaction_Date_{icb_session.num}-"].update(icb_session.transaction_date)
                    icb_session.these_skus = []
                    for sku in skus:
                        icb_session.these_skus.append([f"{sku['Sku']}",f"{sku['Description']}",f"{format_currency(int(sku['Price']))}",f"{sku['Taxable']}"])
                    new_invoice_window[f'-Invoice_Search_Content_{icb_session.num}-'].update(icb_session.these_skus)                    
                elif event_newi == f"-Invoice_Add_Button_{icb_session.num}-":
                    if values[f"-Invoice_Quantity_Input_{icb_session.num}-"] != "":
                        try:
                            quantity = dec(values_newi[f"-Invoice_Quantity_Input_{icb_session.num}-"])
                            this_sku_index = values_newi[f"-Invoice_Search_Content_{icb_session.num}-"]
                            #print(f"""{this_sku_index[0]}""")
                            this_sku_id = icb_session.these_skus[this_sku_index[0]][0]
                            sku_repo = SkuRepository(icb_session.connection)
                            this_sku = sku_repo.get_by_sku(this_sku_id)
                            this_line_item = [f"{this_sku['Sku']}",f"{this_sku['Description']}",f"{format_currency(this_sku['Price'])}",f"{quantity}",format_currency(quantity*int(this_sku['Price']))]
                            if len(icb_session.these_line_items)<10:
                                icb_session.these_line_items.append(this_line_item)
                            else:
                                icb_session.console_log("Maximum number of line items reached.",icb_session.current_console_messages)
                            new_invoice_window[f"-Invoice_Line_Items_{icb_session.num}-"].update(icb_session.these_line_items)
                            populate_invoice_totals(new_invoice_window, values_newi)
                        except Exception as e:
                            print(e)
                elif event_newi == f"-Invoice_Remove_Button_{icb_session.num}-":
                    this_line_index = values_newi[f"-Invoice_Line_Items_{icb_session.num}-"]
                    #print(f"""{this_line_index}""")    
                    if len(this_line_index) > 0: 
                        new_line_items = []
                        for index in range(len(icb_session.these_line_items)):
                            if index != this_line_index[0]:
                                new_line_items.append(icb_session.these_line_items[index])
                        icb_session.these_line_items = new_line_items
                        new_invoice_window[f'-Invoice_Line_Items_{icb_session.num}-'].update(icb_session.these_line_items)
                        populate_invoice_totals(new_invoice_window, values_newi)
                elif event_newi == f"-Submit_Invoice_Button_{icb_session.num}-":
                    if new_invoice_window[f"-Submit_Invoice_Button_{icb_session.num}-"].ButtonText == "Submit" and values_newi[f"-Invoice_Customer_Address_{icb_session.num}-"] != "" and values_newi[f"-Invoice_Status_{icb_session.num}-"] != "" and values_newi[f"-Invoice_Due_Date_{icb_session.num}-"] != "" and icb_session.these_line_items != [] and values_newi[f"-Invoice_SalesTax_{icb_session.num}-"] != "" and values_newi[f"-Invoice_Subtotal_{icb_session.num}-"] != "$0.00" and values_newi[f"-Invoice_Total_{icb_session.num}-"] != "$0.00" and values_newi[f"-Invoice_Debit_{icb_session.num}-"] != "":
                        new_invoice_window[f"-Submit_Invoice_Button_{icb_session.num}-"].update("Really?")
                    elif new_invoice_window[f"-Submit_Invoice_Button_{icb_session.num}-"].ButtonText == "Really?" and values_newi[f"-Invoice_Customer_Address_{icb_session.num}-"] != "" and values_newi[f"-Invoice_Status_{icb_session.num}-"] != "" and values_newi[f"-Invoice_Due_Date_{icb_session.num}-"] != "" and icb_session.these_line_items != [] and values_newi[f"-Invoice_SalesTax_{icb_session.num}-"] != "" and values_newi[f"-Invoice_Subtotal_{icb_session.num}-"] != "$0.00" and values_newi[f"-Invoice_Total_{icb_session.num}-"] != "$0.00" and values_newi[f"-Invoice_Debit_{icb_session.num}-"] != "":
                        
                        
                        icb_session.transaction_debit_account = values_newi[f"-Invoice_Debit_{icb_session.num}-"][:5]
                        icb_session.this_invoice["Invoice_ID"] = f"{this_invoice_id}"
                        icb_session.this_invoice["Line_Items"] = icb_session.these_line_items

                        
                        icb_session.this_invoice["Subtotal"] = values_newi[f"-Invoice_Subtotal_{icb_session.num}-"]
                        icb_session.this_invoice["Sales_Tax"] = values_newi[f"-Invoice_SalesTax_{icb_session.num}-"]
                        icb_session.this_invoice["Total"] = values_newi[f"-Invoice_Total_{icb_session.num}-"]
                        icb_session.this_invoice["Due_Date"] = values_newi[f"-Invoice_Due_Date_{icb_session.num}-"]
                        icb_session.this_invoice["Status"] = values_newi[f"-Invoice_Status_{icb_session.num}-"]
                        icb_session.this_invoice["Customer_ID"] = icb_session.these_customers[values_newi[f"-Invoice_Customers_Results_{icb_session.num}-"][0]][0]
                        icb_session.this_invoice['Tracking_Code'] = id_generator()
                        invoice_date = current_date
                        filepath = generate_new_invoice(new_invoice_window, values_newi, invoice_date)
                        icb_session.this_invoice["Location"] = filepath
                        save_invoice_to_database(new_invoice_window, values_newi, filepath)
                        new_invoice_window.close()
                        update_pos_view(icb_session.window,values)
                        
        elif event == f"-View_POS_Content-":
            #print(f"{values['-View_POS_Content-']}")
            try:
                invoice_index = values['-View_POS_Content-'][0]
                invoice_id = icb_session.invoices[invoice_index][0]
                load_single_invoice(icb_session.window, values, invoice_id)
            except:
                pass
        elif event == "-View_POS_Button-":
            filepath = icb_session.window['-View_POS_Button-'].ButtonText
            try:
                subprocess.call(["xdg-open",filepath]) #linux
            except:
                subprocess.call([filepath],shell=True) #windows

            #Opens the pdf.
        elif event == "-Edit_POS_Button-":
            if icb_session.window['-Edit_POS_Button-'].ButtonText == "Edit Invoice" and values['-POS_Status_Input-'] != "":
                icb_session.window['-POS_Status_Input-'].update(disabled=False)
                icb_session.window['-Edit_POS_Button-'].update("Save Changes")
            elif icb_session.window['-Edit_POS_Button-'].ButtonText == "Save Changes" and values['-POS_Status_Input-'] != "":
                icb_session.window['-POS_Status_Input-'].update(disabled=True)
                icb_session.window['-Edit_POS_Button-'].update("Edit Invoice")
                invoice_id = values['-POS_Number_Display-'][8:]
                invoice_repo = InvoiceRepository(icb_session.connection)
                icb_session.this_invoice = invoice_repo.get_by_id(invoice_id)                   
                #print(f"line 3365 status {icb_session.this_invoice['Status']}")
                if values['-POS_Status_Input-'] == "Overdue" and icb_session.this_invoice['Status'] == 'Due':

                    invoice_repo.update(invoice_id=invoice_id, status='Overdue', edited_time=icb_session.current_time_display[0])
                    icb_session.this_invoice['Status'] = 'Overdue'
                    #print(icb_session.this_invoice)


                    invoice_date = f"{icb_session.this_invoice['Created_Time'].replace('Monday, ','')}"
                    invoice_date = f"{invoice_date.replace('Tuesday, ','')}"
                    invoice_date = f"{invoice_date.replace('Wednesday, ','')}"
                    invoice_date = f"{invoice_date.replace('Thursday, ','')}"
                    invoice_date = f"{invoice_date.replace('Friday, ','')}"
                    invoice_date = f"{invoice_date.replace('Saturday, ','')}"
                    invoice_date = f"{invoice_date.replace('Sunday, ','')}"

                    search=re.search(r" ",invoice_date)
                    invoice_date = invoice_date[:search.start()]
                    icb_session.these_line_items = ast.literal_eval(icb_session.this_invoice['Line_Items'])
                    filepath = generate_new_invoice(icb_session.window,values,invoice_date)
                    update_pos_view(icb_session.window,values)

                elif values['-POS_Status_Input-'] == "Paid" and icb_session.this_invoice['Status'] == 'Due' or values['-POS_Status_Input-'] == "Paid" and icb_session.this_invoice['Status'] == 'Overdue':
                    
                    invoice_id = values['-POS_Number_Display-']
                    #print(invoice_id)
                    check_paid_query = f"""SELECT Transaction_ID from {icb_session.ledger_name} WHERE Name LIKE '{invoice_id}%' AND Debit_Acct IS NOT '10006';"""
                    paid_transactions = db.execute_read_query_dict(icb_session.connection,check_paid_query)

                    invoice_repo = InvoiceRepository(icb_session.connection)
                    icb_session.this_invoice = invoice_repo.get_by_id(invoice_id[8:])
                    icb_session.this_invoice['Status'] = values['-POS_Status_Input-']
                    icb_session.this_invoice['Due_Date'] = f"{current_date}"
                    #print(icb_session.this_invoice['Line_Items'])
                    icb_session.these_line_items = ast.literal_eval(icb_session.this_invoice['Line_Items'])
                    #print(icb_session.these_line_items)
                    if paid_transactions == []:
                        invoice_layout, icb_session.num = invoice_paid_layout(icb_session.num)
                        payment_account_window = sg.Window(title=f"Select Deposit Account", location=(700,200),layout= invoice_layout, margins=(10,2), resizable=True, size=(350,200))
                        payment_account_window.close_destroys_window = True
                        #Save the transaction 
                        while True:
                            event_invoice, values_invoice = payment_account_window.read(close=False)
                            if values_invoice == sg.WIN_CLOSED:
                                break
                            if event_invoice == f'-Invoice_Transactions_Button_{icb_session.num}-':
                                
                                count_transactions_query = f"""SELECT COUNT(*) FROM {icb_session.ledger_name};"""
                                transactions_count = db.execute_read_query_dict(icb_session.connection,count_transactions_query)
                                #print(transactions_count)
                                
                                this_invoice_subtotal = int(dec(f"{icb_session.this_invoice['Subtotal'].replace(",","")}".replace("$",""))*100)
                                accounts_receivable_transaction = int(transactions_count[0]['COUNT(*)'])+1
                                add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
                                Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction}',
                                '10006','{values_invoice[f'-Invoice_Debit_Acct_{icb_session.num}-'][:5]}', '{this_invoice_subtotal}', 'Invoice {icb_session.this_invoice['Invoice_ID']} Paid', 
                                '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
                                '{icb_session.this_invoice['Customer_ID']}');"""
                                added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
                                print(f"added_transaction: {added_transaction}")

                                this_invoice_sales_tax = int(dec(f"{icb_session.this_invoice['Sales_Tax'].replace(",","")}".replace("$",""))*100)
                                add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
                                Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction+1}',
                                '10006','{values_invoice[f'-Invoice_Debit_Acct_{icb_session.num}-'][:5]}', '{this_invoice_sales_tax}', 'Invoice {icb_session.this_invoice['Invoice_ID']} Sales Tax Payable', 
                                '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
                                '{icb_session.this_invoice['Customer_ID']}');"""
                                added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
                                print(f"added_transaction: {added_transaction}")

                                #update the invoice
                                #update the invoice
                                invoice_repo.update(invoice_id=icb_session.this_invoice['Invoice_ID'], status=values[f'-POS_Status_Input-'], edited_time=icb_session.current_time_display[0])
                                update_pos_view(icb_session.window,values)
                                invoice_date = f"{icb_session.this_invoice['Created_Time'].replace('Monday, ','')}"
                                invoice_date = f"{invoice_date.replace('Tuesday, ','')}"
                                invoice_date = f"{invoice_date.replace('Wednesday, ','')}"
                                invoice_date = f"{invoice_date.replace('Thursday, ','')}"
                                invoice_date = f"{invoice_date.replace('Friday, ','')}"
                                invoice_date = f"{invoice_date.replace('Saturday, ','')}"
                                invoice_date = f"{invoice_date.replace('Sunday, ','')}"
                                search=re.search(r" ",invoice_date)
                                invoice_date = invoice_date[:search.start()]
                                generate_new_invoice(icb_session.window,values, invoice_date)
                                payment_account_window.close()
                elif values['-POS_Status_Input-'] == "Refunded" and icb_session.this_invoice['Status'] == 'Paid':
                    
                    invoice_id = values['-POS_Number_Display-']
                    #print(invoice_id)
                    check_paid_query = f"""SELECT Transaction_ID from {icb_session.ledger_name} WHERE Name Like '{invoice_id}%' AND Debit_Acct IS NOT '10006';"""
                    paid_transactions = db.execute_read_query_dict(icb_session.connection,check_paid_query)
                    invoice_repo = InvoiceRepository(icb_session.connection)
                    icb_session.this_invoice = invoice_repo.get_by_id(invoice_id[8:])
                    change_status = icb_session.this_invoice['Status']
                    icb_session.this_invoice['Status'] = values['-POS_Status_Input-']
                    icb_session.this_invoice['Due_Date'] = f"{current_date}"
                    #print(icb_session.this_invoice['Line_Items'])
                    icb_session.these_line_items = ast.literal_eval(icb_session.this_invoice['Line_Items'])
                    #print(icb_session.these_line_items)
                    if paid_transactions != [] and change_status != "Refunded":
                        invoice_layout, icb_session.num = invoice_paid_layout(icb_session.num)
                        payment_account_window = sg.Window(title=f"Select Credit Account", location=(700,200),layout= invoice_layout, margins=(10,2), resizable=True, size=(350,200))
                        payment_account_window.close_destroys_window = True
                        #Save the transaction 
                        while True:
                            event_invoice, values_invoice = payment_account_window.read(close=False)
                            if values_invoice == sg.WIN_CLOSED:
                                break
                            if event_invoice == f'-Invoice_Transactions_Button_{icb_session.num}-':
                                
                                count_transactions_query = f"""SELECT COUNT(*) FROM {icb_session.ledger_name};"""
                                transactions_count = db.execute_read_query_dict(icb_session.connection,count_transactions_query)
                                #print(transactions_count)
                                
                                this_invoice_subtotal = int(dec(f"{icb_session.this_invoice['Subtotal'].replace(",","")}".replace("$",""))*100)
                                accounts_receivable_transaction = int(transactions_count[0]['COUNT(*)'])+1
                                add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
                                Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction}',
                                '{values_invoice[f'-Invoice_Debit_Acct_{icb_session.num}-'][:5]}','15001', '{this_invoice_subtotal}', 'Invoice {icb_session.this_invoice['Invoice_ID']} Refunded', 
                                '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
                                '{icb_session.this_invoice['Customer_ID']}');"""
                                added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
                                print(f"added_transaction: {added_transaction}")

                                this_invoice_sales_tax = int(dec(f"{icb_session.this_invoice['Sales_Tax'].replace(",","")}".replace("$",""))*100)
                                add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
                                Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction+1}',
                                '{values_invoice[f'-Invoice_Debit_Acct_{icb_session.num}-'][:5]}','13003', '{this_invoice_sales_tax}', 'Invoice {icb_session.this_invoice['Invoice_ID']} Sales Tax Payable', 
                                '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
                                '{icb_session.this_invoice['Customer_ID']}');"""
                                added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
                                print(f"added_transaction: {added_transaction}")

                                #update the invoice
                                #update the invoice
                                invoice_repo.update(invoice_id=icb_session.this_invoice['Invoice_ID'], status=values[f'-POS_Status_Input-'], edited_time=icb_session.current_time_display[0])
                                update_pos_view(icb_session.window,values)
                                invoice_date = f"{icb_session.this_invoice['Created_Time'].replace('Monday, ','')}"
                                invoice_date = f"{invoice_date.replace('Tuesday, ','')}"
                                invoice_date = f"{invoice_date.replace('Wednesday, ','')}"
                                invoice_date = f"{invoice_date.replace('Thursday, ','')}"
                                invoice_date = f"{invoice_date.replace('Friday, ','')}"
                                invoice_date = f"{invoice_date.replace('Saturday, ','')}"
                                invoice_date = f"{invoice_date.replace('Sunday, ','')}"
                                search=re.search(r" ",invoice_date)
                                invoice_date = invoice_date[:search.start()]
                                generate_new_invoice(icb_session.window,values, invoice_date)
                                
                                #close the window
                                payment_account_window.close()
                    else:
                        icb_session.console_log("Can't refund unpaid invoice.",icb_session.current_console_messages)
                elif values['-POS_Status_Input-'] == "Canceled" and icb_session.this_invoice['Status'] != "Canceled" and icb_session.this_invoice['Status'] != 'Paid' and icb_session.this_invoice['Status'] != 'Refunded':
                    
                    invoice_id = values['-POS_Number_Display-']
                    #print(invoice_id)
                    check_paid_query = f"""SELECT Transaction_ID from {icb_session.ledger_name} WHERE Name = '{invoice_id}' AND Debit_Acct IS NOT '10006';"""
                    paid_transactions = db.execute_read_query_dict(icb_session.connection,check_paid_query)
                    invoice_repo = InvoiceRepository(icb_session.connection)
                    icb_session.this_invoice = invoice_repo.get_by_id(invoice_id[8:])
                    
                    icb_session.this_invoice['Due_Date'] = f"{current_date}"
                    #print(icb_session.this_invoice['Line_Items'])
                    icb_session.these_line_items = ast.literal_eval(icb_session.this_invoice['Line_Items'])
                    #print(icb_session.these_line_items)
                    if paid_transactions == [] and icb_session.this_invoice['Status'] == "Due" or paid_transactions == [] and icb_session.this_invoice['Status'] == "Overdue":
                                
                        count_transactions_query = f"""SELECT COUNT(*) FROM {icb_session.ledger_name};"""
                        transactions_count = db.execute_read_query_dict(icb_session.connection,count_transactions_query)
                        #print(transactions_count)
                        
                        this_invoice_subtotal = int(dec(f"{icb_session.this_invoice['Subtotal'].replace(",","")}".replace("$",""))*100)
                        accounts_receivable_transaction = int(transactions_count[0]['COUNT(*)'])+1
                        add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
                        Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction}','10006', '15001',
                        '{this_invoice_subtotal}', 'Invoice {icb_session.this_invoice['Invoice_ID']}', 
                        '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
                        '{icb_session.this_invoice['Customer_ID']}');"""
                        added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
                        
                        print(f"added_transaction: {added_transaction}")

                        this_invoice_sales_tax = int(dec(f"{icb_session.this_invoice['Sales_Tax'].replace(",","")}".replace("$",""))*100)
                        accounts_receivable_transaction = int(transactions_count[0]['COUNT(*)'])+2
                        add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Transaction_ID, Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, 
                        Edited_Time, Transaction_Date, Record_Image, Vendor, Customer) VALUES ('{accounts_receivable_transaction}','10006', '13003',
                        '{this_invoice_sales_tax}', 'Invoice {icb_session.this_invoice['Invoice_ID']}', 
                        '{icb_session.this_invoice['Tracking_Code']}', '{icb_session.current_time_display[0]}', '{icb_session.current_time_display[0]}', '{f"{now}"[:10]}', '{icb_session.this_invoice['Location']}', '', 
                        '{icb_session.this_invoice['Customer_ID']}');"""
                        added_transaction = db.execute_query(icb_session.connection, add_transaction_query)
                        
                        print(f"added_transaction: {added_transaction}")

                        icb_session.this_invoice['Status'] = values['-POS_Status_Input-']
                        #update the invoice
                        #update the invoice
                        invoice_repo.update(invoice_id=icb_session.this_invoice['Invoice_ID'], status=values[f'-POS_Status_Input-'], edited_time=icb_session.current_time_display[0])
                        update_pos_view(icb_session.window,values)
                        invoice_date = f"{icb_session.this_invoice['Created_Time'].replace('Monday, ','')}"
                        invoice_date = f"{invoice_date.replace('Tuesday, ','')}"
                        invoice_date = f"{invoice_date.replace('Wednesday, ','')}"
                        invoice_date = f"{invoice_date.replace('Thursday, ','')}"
                        invoice_date = f"{invoice_date.replace('Friday, ','')}"
                        invoice_date = f"{invoice_date.replace('Saturday, ','')}"
                        invoice_date = f"{invoice_date.replace('Sunday, ','')}"
                        
                        search=re.search(r" ",invoice_date)
                        invoice_date = invoice_date[:search.start()]
                        generate_new_invoice(icb_session.window,values, invoice_date)
                    else:
                        icb_session.console_log("Can't cancel paid invoice.",icb_session.current_console_messages)
                else:
                    icb_session.console_log("No changes made to invoice. Check input.",icb_session.current_console_messages)
                    update_pos_view(icb_session.window,values)
        #    window[f"-Business_Receipts_Repository_Label_{num}-"].update(text=f"""Receipts Repository Location: {values[f"-Business_Receipts_Repository_{num}-"]}""")
#--------------------------------------------------
#Test to toggle menu items enabled/disabled
#menu_def[0][1][2] = "&Save Database As"
#window['-Program_Menu-'].update(menu_def)
#--------------------------------------------------



        #elif :

        else:
            function_triggered = False
        if function_triggered == True:
            #Resynchronizes the time
            icb_session.synchronized = synchronize_time(icb_session.window, icb_session.current_time_display)
            if icb_session.synchronized[0] == "Yes":     
                if int(f"""{icb_session.synchronized[1][1][-6:-4]}""") - int(icb_session.current_time_display[1][-6:-4]) > 0:
                    icb_session.current_time_display = icb_session.synchronized[1]
                    icb_session.guitimer = int(f"""{icb_session.synchronized[1][1][-6:-4]}""")
                    icb_session.window['-Current_Time_Display-'].update(icb_session.current_time_display[0])
                    #print(f"""Synchronized: {current_time_display[0]}\n{timer}""")
                    if icb_session.guitimer >0:
                        conditional_s = "s"
                        if icb_session.guitimer == 1:
                            conditional_s = ""
                        icb_session.current_console_messages = icb_session.console_log(f"""Minute update delayed by {icb_session.guitimer} second{conditional_s}.""", icb_session.current_console_messages)
                else:
                    icb_session.guitimer = int(f"""{icb_session.synchronized[1][1][-6:-4]}""")
            else:
                icb_session.guitimer = int(f"""{icb_session.synchronized[1][1][-6:-4]}""")
            
        
icb_session.session_log_connection.close()
if icb_session.connection:
    icb_session.connection.close()
icb_session.window.close()
