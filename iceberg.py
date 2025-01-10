import PySimpleGUI as sg
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


#------------------------------------------Section 1 Date Information

sample_date = parser.parse('2023-04-02')

now= datetime.datetime.now()
current_date = now.date()
current_year = now.year
week_past = current_date - datetime.timedelta(6)



def get_current_time_info():
    """Returns the current time information in string format."""
    weekday = ''
    if datetime.datetime.now().weekday() == 0:
        weekday = "Monday"
    if datetime.datetime.now().weekday() == 1:
        weekday = "Tuesday"
    if datetime.datetime.now().weekday() == 2:
        weekday = "Wednesday"
    if datetime.datetime.now().weekday() == 3:
        weekday = "Thursday"
    if datetime.datetime.now().weekday() == 4:
        weekday = "Friday"
    if datetime.datetime.now().weekday() == 5:
        weekday = "Saturday"
    if datetime.datetime.now().weekday() == 6:
        weekday = "Sunday"


    time_info = time.tzname[time.daylight]

    current_time = f"""{weekday}, {datetime.datetime.now().month}/{datetime.datetime.now().day}/{datetime.datetime.now().year}  -  {format(datetime.datetime.now().hour,'02d')}:{format(datetime.datetime.now().minute,'02d')} {time_info}"""
    current_timestamp = f"""{weekday}, {datetime.datetime.now().month}/{datetime.datetime.now().day}/{datetime.datetime.now().year}  -  {format(datetime.datetime.now().hour, '02d')}:{format(datetime.datetime.now().minute,'02d')}:{format(datetime.datetime.now().second,'02d')} {time_info}"""
    return current_time, current_timestamp





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
        self.vendor_number = int(0)
        self.save_location = False#
        self.account_number = False
        self.window = False
        self.vendors = []
        self.transactions = []
        self.transaction_date = datetime.datetime.now()
        self.all_accounts = []
        self.current_date = f"{datetime.datetime.now().month}/{datetime.datetime.now().day}/{datetime.datetime.now().year}"
        self.business_name = []
        self.business_address = []
        self.owner_name = []
        self.owner_title = []
        self.owner_phone = []
        self.owner_email = []
        self.owner_notes = []
        self.business_ein = []
        self.current_year = now.year
        self.receipts_location = "."
        self.current_console_messages = [f"""Welcome to Iceberg Accounting Suite! Create or open a database to get started."""]
        self.session_filekey, self.session_filename, self.session_save_location= db.encrypt_database("sessions.icbs","decrypt","sessions.icbskey",False,"sessions.icbs")
        session_log_connection = db.create_connection("sessions.icbs")
        self.session_log_connection = db.load_db_to_memory(session_log_connection)
        self.session_filekey, self.session_filename, self.session_save_location= db.encrypt_database("sessions.icbs","encrypt","sessions.icbskey",False,"sessions.icbs")
        self.customer_number = 0
        #print(self.session_filekey)


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

logo = "50666888.png"

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

#GUI Functions

def configure_canvas(event, canvas, frame_id):
    canvas.itemconfig(frame_id, width=canvas.winfo_width())

def configure_frame(event, canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

def delete_widget(widget):
    children = list(widget.children.values())
    for child in children:
        delete_widget(child)
    widget.pack_forget()
    widget.destroy()
    del widget

def new_rows():
    global index
    index += 1
    layout_frame = [[sg.Text("Hello World"), sg.Push(), sg.Button('Delete', key=('Delete', index))]]
    return [[sg.Frame(f"Frame {index:0>2d}", layout_frame, expand_x=True, key=('Frame', index))]]

def format_currency(integer,symbol='$'):
    """Converts an integer number of cents to currency format (string) without a dollar sign (2 digits after the decimal)"""
    initial_string = f"{int(integer)}"
    print(initial_string)
    final_string = ''
    if int(integer) == 0 or integer == "0":
        final_string = f"{symbol}0.00"
    elif initial_string[0]=="-":
        
        if len(initial_string) >=5:
            no_commas = f"({int(integer)*(-1)}"[:-2] + "." + f"{(int(integer)*(-1))}"[-2:] + ")"

            count = 0
            for i in range(len(no_commas)):
                if no_commas[len(no_commas)-i-1] != ')' and no_commas[len(no_commas)-i-1] != '(' and no_commas[len(no_commas)-i-1] != '.':

                    count = count + 1

                elif no_commas[len(no_commas)-i-1] == '.':
                    count = 0    
                
                if no_commas[len(no_commas)-i-1] == '(':
                    final_string = no_commas[len(no_commas)-i-1] + symbol + final_string 
                
                elif count < 4:
                    final_string = no_commas[len(no_commas)-i-1] + final_string
                elif count == 4:
                    count =1
                    final_string = no_commas[len(no_commas)-i-1] + ',' + final_string 
        elif len(initial_string)==3:
            final_string = f"({symbol}0.{initial_string[1:]})"
        elif len(initial_string)==2:
            final_string = f"({symbol}0.0{initial_string[1:]})"

        
    else:

        no_commas = f"{int(integer)}"[:-2] + f"{(int(integer)*(-1))}"[-2:] 
        if len(initial_string) >=3:
            no_commas = f"{int(integer)}"[:-2] + "." + f"{(int(integer)*(-1))}"[-2:] 
            count = 0
            for i in range(len(no_commas)):
                if no_commas[len(no_commas)-i-1] != '.':
                    count = count + 1
                    
                elif no_commas[len(no_commas)-i-1] == '.':
                    count = 0    
                
                if count < 4:
                    final_string = no_commas[len(no_commas)-i-1] + final_string
                elif count == 4:
                    count =1
                    final_string = no_commas[len(no_commas)-i-1] + ',' + final_string 
            final_string = symbol + final_string 
        elif len(initial_string) == 2 :
            final_string = f"{symbol}0.{int(integer)}"
        elif len(initial_string) == 1:
            final_string = f"{symbol}0.0{int(integer)}"
        
    print(final_string)
    return final_string



index = 0




#░▒▓█▓▒░         ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓████████▓▒░ 
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓████████▓▒░  ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓█▓▒░        ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░     
#░▒▓████████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░    ░▒▓█▓▒░      ░▒▓██████▓▒░   ░▒▓██████▓▒░     ░▒▓█▓▒░     
                                                                                     

menu_def = [
    ['&File',['&New Database','&Open Database','&Save Database', '!Save Database &As','Database &Properties','E&xit Iceberg']],
    ['&Dashboard',['&Go to Dashboard']],
    ['&Ledger',['&View Ledger','&New Transaction','!&Search Transactions','!New &Journal Entry','!&Reconcile']],
    ['&Reports',['!&Profit and Loss', '!Profit and Loss by &Month','!&Quarterly Report']],
    ['&Vendors',['&View Vendors', '&New Vendor']],
    ['&Customers',['&View Customers', '!&New Customer','!&Invoicing']],
    ['&Inventories',['!&View Invetories','!&New Lot','!&Point of Sale']],
    ['&Owner Equity',['!&View Equity','!New &Investment', '!New &Withdrawal']],
    ['&Employees',['!&View Employees', '!&Timekeeping', '!&Payroll', '!&Benefits']],
    ['&Taxes',['!&View Taxes','!&Sales Tax','!Schedule &C']],
    ['&Help',['!&Documentation', '!&About']]
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
    [sg.Text(f"""Total Equity must match Net Assets. \nOwner Equity + Revenue - Expenses - Liabilities""", size=(38,2), font=("",7), enable_events=True, key="-Total_Equity_Message-", justification="center", background_color=overview_information_color)],
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
    [sg.Frame("",layout=balance_frame_layout, background_color=overview_information_color)],
]

#Create the chart of accounts display
icb_session.db_name = "Select or Create Database"
chart_of_accounts_text_layout = [
    [sg.Table(values=[],row_height=36, bind_return_key=True, col_widths=[10,32,12,12,12], cols_justification=["c","c","c","c","c"], auto_size_columns=False, headings=["Account_ID", "Name", "Credits", "Debits", "Balance"], num_rows=25, expand_x=True, expand_y=True, font=("",medium_print), enable_events=False, justification="Center", key="-Chart_of_Accounts_Content-", background_color=detailed_information_color)],
]

chart_of_accounts_frame_layout = [
    [sg.Text(f"""{icb_session.db_name}:\n Chart of Accounts""", size=(50,2), justification = "center", expand_x = True, expand_y=True,  font=("",medium_print), enable_events=True, key="-Chart_Of_Accounts_Header-")],
    #[sg.Column([[]],element_justification="center", justification="center")],
    [sg.Frame(f"""""", layout=chart_of_accounts_text_layout, expand_x = True, expand_y=True, key="-Chart_Of_Accounts_Content_Frame-", size=(940,600), element_justification="Center", background_color=overview_information_color)],
    [sg.Push(), sg.OptionMenu(values=["All Accounts","10 Assets","11 Expenses", "12 Withdrawals", "13 Liabilities", "14 Owner Equity", "15 Revenue"], enable_events=True, auto_size_text=True, default_value="All Accounts",key="-Account_Type_Picker-"), sg.Button("View Account", key="-View_Account_Button-", disabled=False), sg.Button("Delete Account", key="-Delete_Account_Button-", disabled=True), sg.Button("New Account", key="-New_Account_Button-", disabled=False)],
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

ledger_year_picker_column_layout = [
        [sg.Text("Year: ", font=("",large_print), size=(14,1)), sg.OptionMenu(values=["CY2024","CY2023"], enable_events=True, auto_size_text=True, default_value="CY2024",key="-Ledger_Year_Picker-")],
]

reports_tab = [
    [sg.Text(font=("",medium_print), size=(133,1))],
    [sg.Text("Reports")],
]


view_vendors_data_height = 30
view_vendors_labels_width = 10
view_vendors_data_width = 30

view_vendors_edit_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"No Vendors", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Name_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Category_Input-")],    

    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Contact_First_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Contact_Last_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Contact_Preferred_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Address_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(12,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Phone_Input-"), sg.OptionMenu(phone_types, pad=view_account_labels_pad+1, size=(8,1), background_color="white", disabled=True, key="-Vendor_PhoneType_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Email_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Website_Input-")],
    [sg.Input(f"0.00", pad=view_account_labels_pad+1, font=("",small_print), size=(view_vendors_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Balance_Input-")],
]



view_vendor_labels_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Text(f"Name: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Name_Display-")],    
    [sg.Text(f"Category: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Category_Display-")],    

    [sg.Text(f"First: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Contact_First_Display-")],
    [sg.Text(f"Last: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Contact_Last_Display-")],
    [sg.Text(f"Preferred: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Contact_Preferred_Display-")],
    [sg.Text(f"Address: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Address_Display-")],

    [sg.Text(f"Phone: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Phone_Display-")],
    [sg.Text(f"Email: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Vendor_Email_Display-")],
    [sg.Text(f"Website: ", font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Vendor_Website_Display-")],
    [sg.Text(f"Balance: ",font=("",small_print), size=(view_vendors_labels_width,1),pad=(0, view_account_labels_pad), justification="left", background_color=overview_information_color, key="-Vendor_Balance_Display-")],
]

view_vendor_frame_layout = [
    [sg.Input(f"Vendor Number", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Vendor_Number_Display-")],    
    [sg.Column(layout=view_vendor_labels_layout, justification = "left", background_color=overview_information_color, size=(view_vendors_labels_width*6,view_vendors_data_height*8)), sg.Column(layout=view_vendors_edit_layout, justification = "left", background_color=overview_information_color, size=(view_vendors_data_width*6,view_vendors_data_height*8) )],
    [sg.Text(f"Memo: ", font=("",small_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Multiline(f"Notes:", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,4),justification="left", background_color=detailed_information_color, key="-Vendor_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Vendor", disabled=True,  key="-Edit_Vendor_Button-")],
]




view_vendors_tab_column_1 = [
    [sg.Frame("Vendor: ", layout=view_vendor_frame_layout, size=(275,600),font=("",medium_print,"bold"), key="-View_Vendor_Frame-", background_color=overview_information_color)],
]

view_vendors_tab_column_2 = [
    [sg.Table(values=[],row_height=36, col_widths=[10,20,20,14,14,14], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, headings=["Vendor No.", "Name", "Contact", "Phone", "Email", "Balance"], num_rows=12, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-View_Vendors_Content-", background_color=detailed_information_color)],
]

vendors_tab = [
    #[sg.Text(font=("",medium_print), size=(133,1), justification="center")],
    [sg.Column(view_vendors_tab_column_1, size=(280,600), element_justification="left"), sg.Column(view_vendors_tab_column_2, size=(960,600), element_justification="center", expand_x=True, expand_y=False)],
    [sg.Push(),sg.Input("",(20,1),disabled=True, enable_events=True, key="-Vendors_Search_Input-"),sg.Button("Search",enable_events=True, disabled=True, key="-Vendors_Search_Button-"), sg.Button("New Vendor",enable_events=True, key="-New_Vendor_Button-"),sg.Button("View Register",enable_events=True, key="-View_Vendor_Register_Button-"),sg.Text(" ")],
]









view_customers_data_height = 30
view_customers_labels_width = 10
view_customers_data_width = 30

view_customers_edit_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Input(f"No Customers", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Name_Input-")],    
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Category_Input-")],    

    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Contact_First_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Contact_Last_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1,font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Contact_Preferred_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Address_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(12,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Phone_Input-"), sg.OptionMenu(phone_types, pad=view_account_labels_pad+1, size=(8,1), background_color="white", disabled=True, key="-Customer_PhoneType_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Email_Input-")],
    [sg.Input(f"", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=detailed_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Website_Input-")],
    [sg.Input(f"0.00", pad=view_account_labels_pad+1, font=("",small_print), size=(view_customers_data_width,1),justification="left", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Balance_Input-")],
]



view_customers_labels_layout = [
    #[sg.Text(f"",font=("",medium_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Text(f"Name: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Name_Display-")],    
    [sg.Text(f"Category: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Category_Display-")],    

    [sg.Text(f"First: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Contact_First_Display-")],
    [sg.Text(f"Last: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Contact_Last_Display-")],
    [sg.Text(f"Preferred: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Contact_Preferred_Display-")],
    [sg.Text(f"Address: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Address_Display-")],

    [sg.Text(f"Phone: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Phone_Display-")],
    [sg.Text(f"Email: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Customer_Email_Display-")],
    [sg.Text(f"Website: ", font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=detailed_information_color, key="-Customer_Website_Display-")],
    [sg.Text(f"Balance: ",font=("",small_print), size=(view_customers_labels_width,1),pad=(0, view_account_labels_pad), justification="left", background_color=overview_information_color, key="-Customer_Balance_Display-")],
]

view_customers_frame_layout = [
    [sg.Input(f"Customer Number", font=("",medium_print), size=(30,1),justification="center", disabled_readonly_background_color=overview_information_color, background_color="white", border_width=edit_account_border_width, readonly=True, key="-Customer_Number_Display-")],    
    [sg.Column(layout=view_customers_labels_layout, justification = "left", background_color=overview_information_color, size=(view_customers_labels_width*6,view_customers_data_height*8)), sg.Column(layout=view_customers_edit_layout, justification = "left", background_color=overview_information_color, size=(view_customers_data_width*6,view_customers_data_height*8) )],
    [sg.Text(f"Memo: ", font=("",small_print), size=(account_information_labels_width,1),justification="left", background_color=overview_information_color)],
    [sg.Multiline(f"Notes:", font=("",medium_print), autoscroll=True, size=(account_information_labels_width*2,4),justification="left", background_color=detailed_information_color, key="-Customer_Notes_Display-")],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Customer", disabled=True,  key="-Edit_Customer_Button-")],
]




view_customers_tab_column_1 = [
    [sg.Frame("Customer: ", layout=view_customers_frame_layout, size=(275,600),font=("",medium_print,"bold"), key="-View_Customer_Frame-", background_color=overview_information_color)],
]

view_customers_tab_column_2 = [
    [sg.Table(values=[],row_height=36, col_widths=[10,20,20,14,14,14], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, headings=["Customer No.", "Name", "Contact", "Phone", "Email", "Balance"], num_rows=12, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-View_Customers_Content-", background_color=detailed_information_color)],
]


customers_tab = [
    #[sg.Text(font=("",medium_print), size=(133,1), justification="center")],
    [sg.Column(view_customers_tab_column_1, size=(280,600), element_justification="left"), sg.Column(view_customers_tab_column_2, size=(960,600), element_justification="center", expand_x=True, expand_y=False)],
    [sg.Push(),sg.Input("",(20,1),disabled=True, enable_events=True, key="-Customers_Search_Input-"),sg.Button("Search",enable_events=True, disabled=True, key="-Customers_Search_Button-"), sg.Button("New Customer",enable_events=True, key="-New_Customer_Button-"),sg.Button("View Register",enable_events=True, key="-View_Customer_Register_Button-"),sg.Text(" ")],
]

invoicing_tab = [
    [sg.Text(font=("",medium_print), size=(133,1))],
    [sg.Text("Invoicing")],

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
    [sg.Table(values=[],row_height=36, col_widths=[16,8,35,11,11,11], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, headings=["Transaction No.", "Date", "Memo", "Credits", "Debits", "Balance"], num_rows=12, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, justification="Center", key="-Account_Register_Content-", background_color=detailed_information_color)],
]


view_account_tab = [
    #[sg.Text(font=("",medium_print), size=(133,1), justification="center")],
    [sg.Column(view_account_tab_column_1, size=(280,460), element_justification="left"), sg.Column(view_account_tab_column_2, size=(960,460), element_justification="center", expand_x=True, expand_y=False)],
    [sg.Push(),sg.Input("",(20,1),disabled=True, enable_events=True, key="-Account_Register_Search_Input-"),sg.Button("Search",enable_events=True, disabled=True, key="-Account_Register_Search_Button-"),sg.Button("View Transaction",enable_events=True, key="-Account_Register_View_Transaction_Button-"),sg.Text(" ")],
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
    [sg.Text("Address"), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Address-",)],
    [sg.Text("Owner or Financial Officer Name:"), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Officer-",)],
    [sg.Text("Title or Position:"), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Officer_Title-",)],
    [sg.Text("Phone Number: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Phone-",)],
    [sg.Text("Email: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_Email-",)],
    [sg.Text("EIN or SSN: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Business_EIN-",)],
    [sg.Text("Receipts Repository: "), sg.Push(), sg.Input("",(25,1),key=f"-Edit_Receipts_Repository-",)],
    [sg.Multiline("Notes: ", size=(62,9),key=f"-Edit_Business_Notes-",)],
    [sg.Push(), sg.FolderBrowse(button_text="Re-Key Database", size=(16,1), enable_events=True, key=f"-Re_Key_Database-", font=("", medium_print)),sg.Button("Save Changes", size=(16,1), font=("", medium_print), enable_events=True, key="-Save_Revised_Properties-")],

]

transaction_information_labels_width = 10

transaction_information_width = 43- transaction_information_labels_width

view_ledger_labels_layout = [
    [sg.Text(f"Name: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Name_Display-")],
    [sg.Text(f"Date: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Date_Display-")],
    [sg.Text(f"Recorded: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Recorded_Display-")],
    [sg.Text(f"Edited: ",font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Edited_Display-")],
    [sg.Text(f"Amount: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Amount_Display-")],
    [sg.Text(f"Debit Acct: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Credit_Display-")],
    [sg.Text(f"Credit Acct: ", font=("",small_print), size=(transaction_information_labels_width,1),pad=(0, view_account_labels_pad),justification="left", background_color=overview_information_color, key="-Ledger_Debit_Display-")],
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
    [sg.Image("50666888.png", key="-Transaction_Image_Button-", size=(258,280),subsample=4,enable_events=True)],
    [sg.Push(background_color=overview_information_color), sg.Button(f"Edit Transaction", disabled=True,  key="-Edit_Transaction_Button-")],
]


view_ledger_tab_column_1 = [
    [sg.Frame("Transaction: ", layout=view_ledger_frame_layout, size=(300,755),font=("",medium_print,"bold"), key="-View_Ledger_Frame-", background_color=overview_information_color)],
]
view_ledger_tab_column_2 = [
    [sg.Text(f"Ledger: None", expand_x=True, font=("",medium_print), justification="center", key="-Ledger_Title_Display-")],
    [sg.Table(values=[],row_height=36, col_widths=[7,44,12,10,10,10], cols_justification=["c","c","c","c","c","c"], auto_size_columns=False, header_font=("",small_print),headings=["Transaction", "Name", "Amount", "Debit Account", "Credit Account", "Date"], num_rows=18, expand_x=True, expand_y=True, font=("",medium_print), enable_events=True, key="-Ledger_Display_Content-", background_color=detailed_information_color)],
    [sg.Push(),sg.Input("",(20,1),disabled=True, enable_events=True, key="-Ledger_Search_Input-"),sg.Button("Search",enable_events=True, disabled=True, key="-Ledger_Search_Button-"),sg.Button("New Transaction",enable_events=True, key="-New_Transaction_Button-"),sg.Text(" ")],

]




ledger_tab = [
    [sg.Column(view_ledger_tab_column_1, size=(300,755), element_justification="left"), sg.Column(view_ledger_tab_column_2, size=(935,755), element_justification="center", expand_x=True, expand_y=False)],
]

#-------------Overall Layout------------------------

current_time = get_current_time_info()
#current_year

layout1 = [
    [sg.Menu(menu_def, key="-Program_Menu-")],
    [sg.Text(f"""No Data Loaded""", key="-Load_Messages-", font=("",large_print), size=(20,1), justification="center", expand_x=True)],
#    [sg.Column([[sg.Text("Year: ", font=("",medium_print)),sg.OptionMenu(values=[f"CY{current_year}"], enable_events=True, auto_size_text=True, default_value=f"CY{current_year}",key="-Year_Picker-")]], justification="center", element_justification="center")],
    [sg.Text(current_time[0], key='-Current_Time_Display-', font=("",medium_print), size=(133,1), justification="center", visible=True, expand_x=True)],
    [sg.TabGroup([
        [sg.Tab('Dashboard', layout=dashboard_tab, key='-Dashboard_Tab-')],
        [sg.Tab('View Ledger', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=ledger_tab, size=(800,800))]], visible=False, pad=2, key='-Ledger_Tab-')],#0
        [sg.Tab('Reports', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=reports_tab, size=(800,800))]], visible=False, pad=2, key='-Reports_Tab-')],#1
        [sg.Tab('Vendors', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=vendors_tab, size=(800,800))]], visible=False, pad=2, key='-Vendors_Tab-')],#2
        [sg.Tab('Customers', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=customers_tab, size=(800,800))]], visible=False, pad=2, key='-Customers_Tab-')],#3
        [sg.Tab('Invoicing', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=invoicing_tab, size=(800,800))]], visible=False, pad=2, key='-Invoicing_Tab-')],#4
        [sg.Tab('Inventory', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=inventory_tab, size=(800,800))]], visible=False, pad=2, key='-Inventory_Tab-')],#5
        [sg.Tab('Owner Equity', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=owner_equity_tab, size=(800,800))]], visible=False, pad=2, key='-Owner_Equity_Tab-')],#6
        [sg.Tab('View Account', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=view_account_tab, size=(800,800))]], visible=False, pad=2, key='-View_Account_Tab-')],#7
        [sg.Tab('Database Properties', layout=[[sg.Column(scrollable=False, vertical_scroll_only=True, expand_x=True, expand_y=True, pad=0, layout=view_properties_tab, size=(800,800))]], visible=False, pad=2, key='-View_Properties_Tab-')],#8    
    ], expand_x=True, expand_y=True, key='-Display_Area-', size=(800,720))   ],
    [sg.Column(console_frame_layout, size=(900,60), expand_x=True, key="-Console_Column-", scrollable=True, vertical_scroll_only=True)], #scrollable=False,
]


tab_keys = ['-Dashboard_Tab-','-Ledger_Tab-','-Reports_Tab-','-Vendors_Tab-','-Customers_Tab-','-Invoicing_Tab-','-Inventory_Tab-','-Owner_Equity_Tab-','-View_Account_Tab-','-View_Properties_Tab-']


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
        [sg.Text("Business Name:", font=("",medium_print)), sg.In(size=(30,1), key=f"-db_name_{num}-", font=("", medium_print)), sg.Text(".icb", font=("", medium_print))],
        [sg.Push(), sg.Text("Filekey Save Location: ", font=("", medium_print)),sg.FolderBrowse(size=(16,1), enable_events=True, key=f"-Save_Location_{num}-", font=("", medium_print))],
        [sg.Text("Address"), sg.Push(), sg.In("",(25,1),key=f"-Business_Address_{num}-",)],
        [sg.Text("Owner or Financial Officer Name:"), sg.Push(), sg.In("",(25,1),key=f"-Business_Officer_{num}-",)],
        [sg.Text("Title or Position:"), sg.Push(), sg.In("",(25,1),key=f"-Business_Officer_Title_{num}-",)],
        [sg.Text("Phone Number"), sg.Push(), sg.In("",(25,1),key=f"-Business_Phone_{num}-",)],
        [sg.Text("Email"), sg.Push(), sg.In("",(25,1),key=f"-Business_Email_{num}-",)],
        [sg.Text("EIN or SSN"), sg.Push(), sg.In("",(25,1),key=f"-Business_EIN_{num}-",)],
        [sg.Push(), sg.Text("Receipts Respository Location: ", key=f"-Business_Receipts_Repository_Label_{num}-"), sg.FolderBrowse("Receipts Folder",font=("",small_print),key=f"-Business_Receipts_Repository_{num}-", enable_events=True)],
        [sg.Multiline("Notes: ", size=(62,9),key=f"-Business_Notes_{num}-",)],
        [sg.Column([[sg.Button(button_text="Submit",size=(20,1),key=f'-Submit_New_Database_Button_{num}-', enable_events=True)],[sg.Sizer(460,60)]],justification="center", size=(480,60),element_justification="center",expand_x=True)],
    ]
    
    return new_database_layout, num


def open_database_layout(num):
    num = num + 1
    open_database_layout = [
        [sg.Text("Filekey Save Location: ", font=("", medium_print)),sg.FileBrowse(size=(20,1), enable_events=True, key=f"-Open_File_{num}-", font=("", medium_print))],
        [sg.Button("Open",key=f'-Open_Database_Button_{num}-', enable_events=True)],
    ]
    
    return open_database_layout, num

def new_transaction_layout(num):
    num = num + 1
    count_transactions_query = f"""SELECT MAX(Transaction_ID) AS [Number_of_Records] FROM {icb_session.ledger_name};"""
    transaction_number = db.execute_read_query_dict(icb_session.connection, count_transactions_query)
    transaction_number_str = "1"
    print(count_transactions_query)
    print("transaction_number")
    print(transaction_number)
    if type(transaction_number) != str:
        num_records = transaction_number[0]['Number_of_Records']
        if num_records == None or num_records == "None":
            num_records = 0
        transaction_number_str = f"""{int(num_records)+1}"""
    retrieve_accounts_query = f"""SELECT * FROM tbl_Accounts;"""
    icb_session.all_accounts = db.execute_read_query_dict(icb_session.connection,retrieve_accounts_query)
    these_accounts = []
    for account in icb_session.all_accounts:
        these_accounts.append(f"""{account['Account_ID']} - {account['Name']}""") 
    retrieve_vendors_query = f"""SELECT * FROM tbl_Vendors;"""
    icb_session.vendors = db.execute_read_query_dict(icb_session.connection,retrieve_vendors_query)
    these_vendors = []
    if len(icb_session.vendors)>0:
        for vendor in icb_session.vendors:
            these_vendors.append(f"""{vendor['Vendor_ID']} - {vendor['Business_Name']}""") 
            print("vendors")
            print(icb_session.vendors)
    else:
        these_vendors.append("None")
    new_transaction_column_1 = [
        [sg.Image("CHECKBOOK_ART_FREE_LICENCE_NO_COMMERCIAL.png",size=(50,50),subsample=1),sg.Text(f"Transaction {transaction_number_str}", size=(13,1), font=("Bold",large_print),justification="center", pad=(0,0), key=f"-Transaction_Title_{num}-")],
        [sg.Text("Transaction Name: ", font=("",medium_print)), sg.Push(), sg.Input(size=(20,1), key=f"-Transaction_Name_{num}-", font=("", medium_print) )],
        [sg.Text("Transaction Date: ", font=("",medium_print)), sg.Push(),sg.Input("",size=(12,1),font=("",medium_print), key=f"-Transaction_Date_String_{num}-"), sg.CalendarButton(f"Select Date",format= "%Y-%m-%d", size=(16,1),key=f"-Transaction_Date_{num}-", enable_events=True)],
        [sg.Text("Amount: ", font=("",medium_print)), sg.Push(), sg.Text("$",size=(1,1),font=("",medium_print)), sg.Input("",(16,1),key=f"-Transaction_Amount_{num}-")],
        [sg.Text("Debit Account: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(these_accounts,key=f"-Transaction_Debit_Account_{num}-", enable_events=False)],
        [sg.Text("Credit Account: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(these_accounts,key=f"-Transaction_Credit_Account_{num}-", enable_events=False)],
        [sg.Text("Vendor: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(these_vendors,key=f"-Transaction_Vendor_{num}-")],
        [sg.Text("Customer: ", font=("",medium_print)), sg.Push(), sg.OptionMenu(["","Pauli Portabello","Sally Swiss Chard","Officer Acorn Squash"],key=f"-Transaction_Customer_{num}-")],
        [sg.Multiline("Notes: ", font=("",medium_print), size=(44,4),key=f"-Transaction_Notes_{num}-")],
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
        [sg.Image("CHECKBOOK_ART_FREE_LICENCE_NO_COMMERCIAL.png",size=(50,50),subsample=1),sg.Text(f"New Account", size=(13,1), font=("Bold",large_print),justification="center", key=f"-Account_Title_{num}-")],
        [sg.Text("Account Name: ", font=("",medium_print)), sg.Push(), sg.Input(size=(20,1), key=f"-Account_Name_{num}-", font=("", medium_print) )],
        [sg.Text("Account Type: ", font=("",medium_print)), sg.Push(), sg.Push(), sg.OptionMenu(values=["10 Assets","11 Expenses", "12 Withdrawals", "13 Liabilities", "14 Owner Equity", "15 Revenue"], enable_events=False, auto_size_text=True, default_value="10 Assets",key=f"-Account_Type_Picker_{num}-")],
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
        [sg.Text("Business Name: ", font=("",medium_print)), sg.Push(), sg.Input("",(30,1),key=f"-Vendor_Name_{num}-",)],
        [sg.Text("Merchant Category: ", font=("",medium_print)), sg.Push(), sg.Input("",(30,1),key=f"-Vendor_Category_{num}-",)],
        [sg.Text("Contact First Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Contact_First_{num}-", size=(30,1))],
        [sg.Text("Contact Last Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Contact_Last_{num}-", size=(30,1))],
        [sg.Text("Contact Preferred Name: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Contact_Preferred_{num}-", size=(30,1))],
        [sg.Text("Phone:", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Phone_{num}-", size=(17,1)), sg.OptionMenu(phone_types,"Mobile",key=f"-Vendor_Phone_Type_{num}-")],
        [sg.Text("Address: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Vendor_Address_{num}-", size=(30,1))],
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
        [sg.Text("Address: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Customer_Address_{num}-", size=(30,1))],
        [sg.Text("Email: ", font=("",medium_print)), sg.Push(), sg.Input(key=f"-Customer_Email_{num}-", size=(30,1))],
        [sg.Multiline("Notes: ", font=("",medium_print), size=(62,4),key=f"-Customer_Notes_{num}-",)],
        [sg.Column([[sg.Button(button_text="Add Customer",size=(20,1),key=f'-Submit_Customer_Button_{num}-', enable_events=True)],[sg.Sizer(460,60)]],justification="center", size=(480,60),element_justification="center",expand_x=True)],

    ]
    
    return new_customer_layout, num    


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
if False:
    def generate_filekey(db_name, save_location):
        key = Fernet.generate_key()
        if save_location[-1] != "/":
            save_location = save_location + "/"
        filename = f'{db_name}key'    
        file_address = f'{save_location}{db_name}key'
        with open(file_address, 'wb') as filekey:
            filekey.write(key)#-----------------------------------------------------------------------
        return key, filename

    def encrypt_database(db_name, mode, filename, save_location, new_name):
        """Encrypts or decrypts a database file. 
        Mode is 'encypt' or 'decrypt'. 
        filekey=False will generate a new filekey.
        save_location=False will save to the Iceberg directory."""
        print(f"encrypt db_name {db_name}; mode: {mode}; filename: {filename}; save_location: {save_location}")
        
        db_name_2 = db_name
        if new_name:
            db_name_2 = new_name
        
        if save_location == False or save_location == "" or save_location == ".":
            save_location = "./"
        if save_location[-1] != "/":
            save_location = save_location + "/"
        if filename == False and mode == "encrypt":
            filekey, filename = generate_filekey(db_name, save_location)
        elif filename== False and mode =="decrypt":
            return "Error: Attempted decryption without key.", ""
        if mode == "encrypt":
            with open(f'{save_location}{filename}','rb') as file:
                filekey = file.read()        
            #print('filekey generated')
            #print(filekey)
            fernet=Fernet(filekey)
            with open(f'./{db_name_2}','rb') as file:
                original_db = file.read()
            #print(original_db)
            encrypted_db = fernet.encrypt(original_db)
            with open(f'./{db_name}','wb') as encrypted_file:
                encrypted_file.write(encrypted_db)
            return filekey, filename, save_location
        elif mode == "decrypt":
            with open(f'{save_location}{filename}','rb') as file:
                filekey = file.read()  
            fernet=Fernet(filekey)
            with open(f'./{db_name}','rb') as file:
                original_db = file.read()
            print(filekey)
            encrypted_db = fernet.decrypt(original_db)
            with open(f'./{db_name_2}','wb') as encrypted_file:
                encrypted_file.write(encrypted_db)
            return filekey, filename, save_location
        else:
            return "Error: Mode not selected. (encrypt or decrypt)", ""


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
        if db_name_1[chara] == " " or db_name_1[chara] == "." or db_name_1[chara] == "," or db_name_1[chara] == "/" or db_name_1[chara] == "-":
            db_name_2 = db_name_2 + "_"
        else:
            db_name_2 = db_name_2 + db_name_1[chara]
    icb_session.db_name = db_name_2 + """.icb"""
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
    #print(f"{created_table}: tbl_Console_Log")


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
                """, Vendor INT(16)""",
                """, Customer INT(16)""",
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

    create_table_2_query = f"""CREATE TABLE tbl_Accounts (Account_ID INTEGER NOT NULL"""
    lines = [   """, Name VARCHAR(9999) NOT NULL UNIQUE""",
                """, Notes VARCHAR(9999)""",
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, Institution VARCHAR(9999)""",
                """, Ins_Account_Type VARCHAR(9999)""",
                """, Ins_Routing_Number VARCHAR(9999)""",
                """, Ins_Account_Number VARCHAR(9999)""",
                """, PRIMARY KEY ("Account_ID")"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_2_query = create_table_2_query + lines[p]
    create_table_2_query = create_table_2_query + """);"""


    created_table = db.create_tables(icb_session.connection,create_table_2_query)
    print(created_table)

    #TODO:ADD IN DEFAULT ACCOUNTS


    default_accounts = [
        [10001,"Fixed Asset Real Estate","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10002,"Fixed Asset Bank Account Checking","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10003,"Misc Property","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10004,"Petty Cash","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [10005,"Product Inventory","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
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
        [14001,"Owner Equity","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [15001,"Product Sales","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [15002,"Service Sales","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [15003,"Real Estate Equity","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
        [15004,"Other Revenue","Notes:",icb_session.current_time_display[0],icb_session.current_time_display[0],"","","",""],
    ]

    for account in default_accounts:
        create_default_accounts_query = f"""INSERT INTO tbl_Accounts (Account_ID, Name, Notes,Created_Time, Edited_Time, Institution, Ins_Account_Type, Ins_Routing_Number, Ins_Account_Number)
            VALUES(({account[0]}),("{account[1]}"),("{account[2]}"),("{account[3]}"),("{account[4]}"),("{account[5]}"),("{account[6]}"),("{account[7]}"),("{account[8]}"));
        """
        #print(create_default_accounts_query)
        created_account = db.execute_query(icb_session.connection,create_default_accounts_query)
        current_console_messages = icb_session.console_log(message=created_account,current_console_messages=current_console_messages)
        print(created_account)


    #3 Create the Owners table

    create_table_3_query = f"""CREATE TABLE tbl_Owners (Owner_ID INTEGER NOT NULL"""
    lines = [   """, First_Name VARCHAR(9999) NOT NULL""",
                """, Middle_Name VARCHAR(9999)""",
                """, Last_Name VARCHAR(9999) NOT NULL""",
                """, Preferred_Name VARCHAR(9999) NOT NULL""",
                """, Full_Name VARCHAR(9999) NOT NULL""",
                """, Phone_Number VARCHAR(9999)""",
                """, Phone_Number_Type VARCHAR(9999)""",
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, Home_Address VARCHAR(9999)""",
                """, Record_Location VARCHAR(9999) NOT NULL""",
                """, Email VARCHAR(9999)""",
                """, PRIMARY KEY ("Owner_ID" AUTOINCREMENT)"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_3_query = create_table_3_query + lines[p]
    create_table_3_query = create_table_3_query + """);"""


    created_table = db.create_tables(icb_session.connection,create_table_3_query)
    print(created_table)


    #TODO: Collect user information during setup

    #4 Create the Vendors Table
    create_table_4_query = f"""CREATE TABLE tbl_Vendors (Vendor_ID INTEGER NOT NULL"""
    
    lines = [   """, Business_Name VARCHAR(9999) NOT NULL UNIQUE""",   
                """, Merchant_Category VARCHAR(9999) NOT NULL""",   
                """, Contact_First_Name VARCHAR(9999) NOT NULL""",
                """, Contact_Last_Name VARCHAR(9999) NOT NULL""",
                """, Preferred_Name VARCHAR(9999) NOT NULL""",
                """, Phone_Number VARCHAR(9999)""",
                """, Phone_Number_Type VARCHAR(9999)""",   #Mobile, Home, Office, Work, Other
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, Business_Address VARCHAR(9999)""",
                """, Business_Email VARCHAR(9999)""",
                """, Business_Website VARCHAR(9999)""",
                """, Notes VARCHAR(9999)""",
                """, PRIMARY KEY ("Vendor_ID")"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_4_query = create_table_4_query + lines[p]
    create_table_4_query = create_table_4_query + """);"""

    icb_session.vendor_number = int(0)
    created_table = db.create_tables(icb_session.connection,create_table_4_query)
    print(created_table)

    #5 Create the Customers Table
    create_table_5_query = f"""CREATE TABLE tbl_Customers (Customer_ID INTEGER NOT NULL """
    
    lines = [   """, Customer_First_Name VARCHAR(9999) NOT NULL""",
                """, Customer_Last_Name VARCHAR(9999) NOT NULL""",
                """, Customer_Company_Name VARCHAR(9999)""",
                """, Customer_Retail_Certificate VARCHAR(9999)""",
                """, Preferred_Name VARCHAR(9999) NOT NULL""",
                """, Customer_Phone_Number VARCHAR(9999)""",
                """, Customer_Phone_Number_Type VARCHAR(9999)""",
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, Customer_Address VARCHAR(9999)""",
                """, Customer_Email VARCHAR(9999)""",
                """, PRIMARY KEY ("Customer_ID" AUTOINCREMENT)"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_5_query = create_table_5_query + lines[p]
    create_table_5_query = create_table_5_query + """);"""


    db.create_tables(icb_session.connection,create_table_5_query)
    print(created_table)

    #6 Create the Invoices Table
    create_table_7_query = f"""CREATE TABLE tbl_Invoices (Invoice_ID INTEGER NOT NULL"""
    
    lines = [   """, Customer_ID INT(16) NOT NULL""",
                """, Line_Items VARCHAR(9999) NOT NULL""", #Format as List, parse on read
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, Invoice_Total DECIMAL(10,2) NOT NULL""",
                """, Paid_Status VARCHAR(6) NOT NULL""",
                """, Payment_Method VARCHAR(9999) NOT NULL""",
                """, PRIMARY KEY ("Invoice_ID" AUTOINCREMENT)"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_7_query = create_table_7_query + lines[p]
    create_table_7_query = create_table_7_query + """);"""


    created_table = db.create_tables(icb_session.connection,create_table_7_query)
    #print("Invoices_Table")
    print(created_table)



    #8 Create the Properties Table
    create_table_8_query = f"""CREATE TABLE tbl_Properties (Property_ID INTEGER NOT NULL"""
    
    lines = [   """, Property_Name VARCHAR(9999) NOT NULL""", 
                """, Property_Value VARCHAR(9999) NOT NULL""", 
                """, Property_Units VARCHAR(9999) NOT NULL""", 
                """, Created_Time VARCHAR(9999) NOT NULL""", 
                """, Edited_Time VARCHAR(9999) NOT NULL""" ,
                """, PRIMARY KEY ("Property_ID" AUTOINCREMENT)"""
            ]
    num_lines = len(lines)
    for p in range(num_lines):
        create_table_8_query = create_table_8_query + lines[p]
    create_table_8_query = create_table_8_query + """);"""


    created_table = db.create_tables(icb_session.connection,create_table_8_query)
    #print("Invoices_Table")
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
    icb_session.receipts_location = values[f'-Business_Receipts_Repository_{num}-']

    database_properties = [
        ["Business Name",f"{icb_session.business_name}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Address",f"{icb_session.business_address}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Owner or Financial Officer Name",f"{icb_session.owner_name}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Title or Position",f"{icb_session.owner_title}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Phone Number",f"{icb_session.owner_phone}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Email",f"{icb_session.owner_email}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Notes",f"{icb_session.owner_notes}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["EIN or SSN",f"{icb_session.business_ein}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Receipts Repository Location",f"{icb_session.receipts_location}","",icb_session.current_time_display[0],icb_session.current_time_display[0]],
        ["Ledger Name",icb_session.ledger_name,"",icb_session.current_time_display[0],icb_session.current_time_display[0]],
    ]

    for property in database_properties:
        create_properties_query = f"""INSERT INTO tbl_Properties (Property_Name, Property_Value, Property_Units,Created_Time, Edited_Time)
            VALUES(("{property[0]}"),("{property[1]}"),("{property[2]}"),("{property[3]}"),("{property[4]}"));
        """
        #print(create_default_accounts_query)
        created_property = db.execute_query(icb_session.connection,create_properties_query)
        print(create_properties_query)
        print(created_property)

    icb_session.current_console_messages = icb_session.console_log(message=f"Saved database properties for {icb_session.business_name}. Owner: {icb_session.owner_name}",current_console_messages=icb_session.current_console_messages)





    #Condition Save Location
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
    



#def load_dashboard_initial(connection, window, values):
        #Load the dashboard

#    update_dashboard_statistics(connection, window)




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
    start_date = f"{(icb_session.current_year)}-01-01"
    end_date = f"{(icb_session.current_year)+1}-01-01"

    #Read the database
    read_ledger_query = f"""SELECT * FROM {icb_session.ledger_name};""" # WHERE Transaction_Date >= '{start_date}' AND Transaction_Date < '{end_date}'
    print(read_ledger_query)
    current_year_ledger = db.execute_read_query_dict(icb_session.connection, read_ledger_query)
    print(type(current_year_ledger))
    print(f"read the ledger: {current_year_ledger}")
    if type(current_year_ledger) == str:
        current_year_ledger = False
    read_accounts_query = f"""SELECT * from tbl_Accounts;"""
    accounts = db.execute_read_query_dict(icb_session.connection, read_accounts_query)
    #print(accounts)
    #Create and display the chart of accounts.
    chart_of_accounts_display_content = []
    for account in accounts:
        account_type = 1
        account_Id = str(account['Account_ID'])
        account_Name = str(account['Name'])
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
                if debit_account == account_Id:
                    debits = debits + amount
                    balance = account_type*(debits - credits)
                elif credit_account == account_Id:
                    credits = credits + amount
                    balance = account_type*(debits - credits)
        credits =  format_currency(credits)
        debits = format_currency(debits)
              
        balance = format_currency(balance)
        
        chart_of_accounts_display_content.append([account_Id,account_Name,credits, debits, balance])
    window['-Chart_of_Accounts_Content-'].update(chart_of_accounts_display_content)

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

    owner_equity_report = f"""Owner_Equity: {owner_equity_display}"""
    window["-Equity_Report-"].update(owner_equity_report)

    total_equity_report = f"""Owner_Equity: {total_equity_display}"""
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

    #latest_year = window["-Year_Picker-"].values[-1] #Comment out the year picker

    

    return window, chart_of_accounts_display_content







def load_database_properties_tab(window, values, connection):
    if connection==False:
        print("Error: load_database_properties_tab did not execute. Not connected to database.")
    else:

        retrieve_properties_query = f"""SELECT * FROM tbl_Properties"""

        current_properties = db.execute_read_query_dict(connection, retrieve_properties_query)
        print(current_properties)
        for property in current_properties:
            property_name = property['Property_Name']
            property_value = property['Property_Value']
            if property_name == "Business Name":
                window['-edit_db_name-'].update(property_value)
            elif property_name == "Address":
                window['-Edit_Business_Address-'].update(property_value)
            elif property_name == "Owner or Financial Officer Name":
                window['-Edit_Business_Officer-'].update(property_value)
            elif property_name == "Title or Position":
                window['-Edit_Business_Officer_Title-'].update(property_value)
            elif property_name == "Phone Number":
                window['-Edit_Business_Phone-'].update(property_value)
            elif property_name == "Email":
                window['-Edit_Business_Email-'].update(property_value)
            elif property_name == "Notes":
                window['-Edit_Business_Notes-'].update(property_value)
            elif property_name == "EIN or SSN":
                window['-Edit_Business_EIN-'].update(property_value)
            elif property_name == "Receipts Repository Location":
                window['-Edit_Receipts_Repository-'].update(property_value)

def load_view_account_tab(window, values, account_number, ledger_name):
    """Loads the selected account from the chart of accounts."""
    this_account_query = f"""SELECT * FROM tbl_Accounts WHERE Account_ID IS {account_number};"""
    
    this_account_0 = db.execute_read_query_dict(icb_session.connection, this_account_query)
    print(f'this_account: {this_account_0}')
    this_account = this_account_0[0]
    

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
                display_transactions.append([transaction["Transaction_ID"],transaction["Transaction_Date"],transaction["Notes"],"$0.00",transaction_amount,this_account_balance_formatted])
            elif f"{transaction['Credit_Acct']}" == f"{account_number}":
                this_account_balance = this_account_balance - int(transaction['Amount'])*sign_convention
                this_account_credits = this_account_credits + int(transaction['Amount'])
                this_account_balance_formatted = format_currency(this_account_balance)
                display_transactions.append([transaction["Transaction_ID"],transaction["Transaction_Date"],transaction["Notes"],transaction_amount,"$0.00",this_account_balance_formatted])
            
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
    
    
    
    
    update_account_query = f"""UPDATE tbl_Accounts SET Name = '{values['-Edit_Account_Name_Input-']}', Notes = '{values['-Account_Notes_Display-']}', Edited_Time = '{current_time[1]}', Institution = '{values['-Edit_Account_Bank-']}', Ins_Account_Number = '{values['-Edit_Account_Bank_Acct_Number-']}', Ins_Account_Type = '{values['-Edit_Account_Bank_Acct_Type-']}', Ins_Routing_Number = '{values['-Edit_Account_Bank_Acct_Routing-']}' WHERE Account_ID = {values['-Edit_Account_Number_Input-']};"""
    updated_account = db.execute_query(icb_session.connection, update_account_query)
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

    add_vendor_query = f"""INSERT INTO tbl_Vendors (Vendor_ID, Business_Name, Merchant_Category, Contact_First_Name, Contact_Last_Name, Preferred_Name, Phone_Number, Phone_Number_Type, Created_Time, Edited_Time, Business_Address, Business_Email, Business_Website,Notes)
    VALUES ({add_vendor_number},"{add_vendor_name}","{add_vendor_category}","{add_vendor_contact_first}","{add_vendor_contact_last}","{add_vendor_contact_preferrred}","{add_vendor_phone}","{add_vendor_phone_type}","{current_time[1]}","{current_time[1]}","{add_vendor_address}","{add_vendor_email}","{add_vendor_website}","{add_vendor_notes}");"""

    added_vendor = db.execute_query(icb_session.connection,add_vendor_query)

    icb_session.current_console_messages = icb_session.console_log(f"Added Vendor {add_vendor_number}: {added_vendor}",icb_session.current_console_messages)

def load_single_vendor(window,values, vendor):
    this_vendor_query = f"""Select * FROM tbl_Vendors WHERE Vendor_ID = {vendor[0]};"""
    retrieved_vendor = db.execute_read_query_dict(icb_session.connection,this_vendor_query)
    if type(retrieved_vendor) == str:
        print(retrieved_vendor)
    else:  
        #print("retrieved_vendor[0]")
        #print(retrieved_vendor[0]['Vendor_ID'])
        window['-Vendor_Name_Input-'].update(retrieved_vendor[0]['Business_Name'])
        window['-Vendor_Category_Input-'].update(retrieved_vendor[0]['Merchant_Category'])
        window['-Vendor_Contact_First_Input-'].update(retrieved_vendor[0]['Contact_First_Name'])
        window['-Vendor_Contact_Last_Input-'].update(retrieved_vendor[0]['Contact_Last_Name'])
        window['-Vendor_Contact_Preferred_Input-'].update(retrieved_vendor[0]['Preferred_Name'])
        window['-Vendor_Address_Input-'].update(retrieved_vendor[0]['Business_Address'])
        window['-Vendor_Phone_Input-'].update(retrieved_vendor[0]['Phone_Number'])
        window['-Vendor_PhoneType_Input-'].update(f"({retrieved_vendor[0]['Phone_Number_Type']})")        
        window['-Vendor_Email_Input-'].update(retrieved_vendor[0]['Business_Email'])
        window['-Vendor_Website_Input-'].update(retrieved_vendor[0]['Business_Website'])
        window['-Vendor_Notes_Display-'].update(retrieved_vendor[0]['Notes'])

def load_vendors_tab(window,values):
    """Loads the vendors tab on the gui"""
    icb_session.vendors = []
    load_vendors_query = f"""SELECT * FROM tbl_Vendors;"""
    retrieved_vendors = db.execute_read_query_dict(icb_session.connection,load_vendors_query)
    if len(retrieved_vendors) > 0:
        #print(retrieved_vendors[0]['Vendor_ID'])
        
        for vendor in retrieved_vendors:
            icb_session.vendors.append([f"{vendor['Vendor_ID']}",f"{vendor['Business_Name']}",f"{vendor['Preferred_Name']}",f"{vendor['Phone_Number']} ({vendor['Phone_Number_Type']})",f"{vendor['Business_Email']}", '$0.00'])
        window["-View_Vendors_Content-"].update(icb_session.vendors)
        print(icb_session.vendors)
    else:
        icb_session.current_console_messages = icb_session.console_log("Add a new Vendor to the database to get started.",icb_session.current_console_messages)



def get_customer(window, values, customer_id):
    """Retrieves customer data from the database."""
    customer_query = f"""SELECT * FROM tbl_Customers WHERE Customer_ID = '{customer_id}';"""
    customer = db.execute_read_query_dict(icb_session.connection,customer_query)
    #print(customer)
    if len(customer) < 1:
        return "None"
    else:
        return customer

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

    add_customer_query = f"""INSERT INTO tbl_Customers (Customer_ID, Customer_Company_Name,  Customer_First_Name, Customer_Last_Name, Preferred_Name, Customer_Phone_Number, Customer_Phone_Number_Type, Created_Time, Edited_Time, Customer_Address, Customer_Email, Notes)
    VALUES ({add_customer_number},"{add_customer_company_name}","{add_customer_contact_first}","{add_customer_contact_last}","{add_customer_contact_preferrred}","{add_customer_phone}","{add_customer_phone_type}","{current_time[1]}","{current_time[1]}","{add_customer_address}","{add_customer_email}","{add_customer_notes}");"""

    added_customer = db.execute_query(icb_session.connection,add_customer_query)

    icb_session.current_console_messages = icb_session.console_log(f"Added Customer {add_customer_number}: {added_customer}",icb_session.current_console_messages)


def load_ledger_tab(window, values):
    """Loads transactions into the Ledger."""
    transactions_query = f"SELECT * FROM {icb_session.ledger_name};"
    print(transactions_query)
    icb_session.transactions = []
    print(icb_session.transactions)
    these_transactions = db.execute_read_query_dict(icb_session.connection,transactions_query)
    print(these_transactions)
    if len(these_transactions) > 0 and type(these_transactions) == list:        
        for transaction in these_transactions:
            retrieved_customer = get_customer(icb_session.window,values,transaction['Customer'])
            customer_name = "None"
            if retrieved_customer != "None":
                print(retrieved_customer)
                customer_name = f"{retrieved_customer['Customer_First_Name']} {retrieved_customer['Customer_Last_Name']} ({retrieved_customer['Preferred_Name']})"
            
            icb_session.transactions.append([f"{transaction['Transaction_ID']}",f"{transaction['Name']}",f"{format_currency(int(transaction['Amount']))}",f"{transaction['Debit_Acct']}",f"{transaction['Credit_Acct']}", f"{transaction['Transaction_Date']}"])
        icb_session.window["-Ledger_Display_Content-"].update(icb_session.transactions)
        icb_session.window['-Ledger_Title_Display-'].update(icb_session.ledger_name)
    

    else:
        #icb_session.transactions = []
        icb_session.current_console_messages = icb_session.console_log("Add a new Transaction to the database to get started.",icb_session.current_console_messages)

def load_transaction_details(transaction_number):
    print(transaction_number)
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
    icb_session.window['-Transaction_Image_Button-'].update(transaction[0]['Record_Image'])

def add_transaction_to_database(values):
    """Adds a transaction to the database."""
    current_time = get_current_time_info()

    print(icb_session.transaction_date)
    this_credit_account = int(values[f'-Transaction_Credit_Account_{icb_session.num}-'][0:5])
    this_debit_account = int(values[f"-Transaction_Debit_Account_{icb_session.num}-"][0:5])
    this_amount = int(dec(values[f"-Transaction_Amount_{icb_session.num}-"])*100)
    print("this_amount")
    print(this_amount)
    this_name = values[f"-Transaction_Name_{icb_session.num}-"]
    this_notes = values[f"-Transaction_Notes_{icb_session.num}-"]
    this_image = values[f"-Transaction_Image_Input_{icb_session.num}-"]
    if this_image[-4:] == ".pdf":
        this_image = this_image[:-4]+'_0.png'
    this_vendor = values[f"-Transaction_Vendor_{icb_session.num}-"]
    this_customer = values[f"-Transaction_Customer_{icb_session.num}-"]
    this_transaction_date = values[f'-Transaction_Date_String_{icb_session.num}-']
    add_transaction_query = f"""INSERT INTO {icb_session.ledger_name} (Credit_Acct, Debit_Acct, Amount, Name, Notes, Created_Time, Edited_Time, Transaction_Date, Record_Image, Vendor, Customer)
    VALUES ({this_credit_account},{this_debit_account},{this_amount},"{this_name}","{this_notes}","{current_time[1]}","{current_time[1]}","{this_transaction_date}","{this_image}","{this_vendor}","{this_customer}");"""
    print(add_transaction_query)
    added_transaction = db.execute_query(icb_session.connection,add_transaction_query)
    print(added_transaction)
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
            print(images_from_path)
            # Do something here
            remove_to = image_url[::-1].index("/")
            #print(remove_to)
            image_location = image_url[:len(image_url)-remove_to]
            print(image_url)
            print(image_location)
            image_name_0 = image_url[-remove_to:]            
            image_name = image_name_0[:-4]
            print(image_name)
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
    print(current_time)
    account_type = int(values[f'-Account_Type_Picker_{icb_session.num}-'][:2])
    print(account_type)

    count_accounts_query = f"""SELECT COUNT(Account_ID) AS [Number_of_Records] FROM tbl_Accounts WHERE Account_ID > {account_type}000 AND Account_ID < {account_type+1}000;"""
    account_count = db.execute_read_query_dict(icb_session.connection, count_accounts_query)
    print("account_count")
    print(account_count)
    new_account_number = 0
    if type(new_account_number) != str:
        new_account_number = int(f"{account_type}001")+int(account_count[0]['Number_of_Records'])
        print(count_accounts_query)
        print("account_number")
        print(new_account_number)
        account_number_str = ""
        if type(new_account_number) != str:
            account_number_str = f"""{new_account_number}"""
        
        new_account_name = values[f"-Account_Name_{icb_session.num}-"]
        new_account_notes = values[f"-Account_Notes_{icb_session.num}-"]
        new_account_bank = values[f"-Account_Bank_{icb_session.num}-"]
        new_account_bank_type = values[f"-Account_Bank_Account_Type_{icb_session.num}-"]
        new_account_routing = values[f"-Account_Bank_Account_Number_{icb_session.num}-"]
        new_account_bank_account_number = values[f"-Account_Name_{icb_session.num}-"]
        new_account = [
            [new_account_number,new_account_name,new_account_notes,current_time[1],current_time[1],new_account_bank,new_account_bank_type,new_account_routing,new_account_bank_account_number],
        ]

        for account in new_account:
            create_default_accounts_query = f"""INSERT INTO tbl_Accounts (Account_ID, Name, Notes,Created_Time, Edited_Time, Institution, Ins_Account_Type, Ins_Routing_Number, Ins_Account_Number)
                VALUES(({account[0]}),("{account[1]}"),("{account[2]}"),("{account[3]}"),("{account[4]}"),("{account[5]}"),("{account[6]}"),("{account[7]}"),("{account[8]}"));
            """
            #print(create_default_accounts_query)
            created_account = db.execute_query(icb_session.connection,create_default_accounts_query)
            icb_session.current_console_messages = icb_session.console_log(message=created_account,current_console_messages=icb_session.current_console_messages)
            print(created_account)
    else:
        icb_session.current_console_messages = icb_session.console_log(message=account_count,current_console_messages=icb_session.current_console_messages)


def update_chart_of_accounts(window, values, acct_types):
    if acct_types == "All Accounts":
        update_dashboard_statistics(window,values)
    else:
        read_ledger_query = f"""SELECT * FROM {icb_session.ledger_name} WHERE Credit_Acct LIKE '{acct_types}%' OR Debit_Acct LIKE '{acct_types}%';"""
        #Read the database
        #read_ledger_query = f"""SELECT * FROM {icb_session.ledger_name};""" # WHERE Transaction_Date >= '{start_date}' AND Transaction_Date < '{end_date}'
        print(read_ledger_query)
        current_year_ledger = db.execute_read_query_dict(icb_session.connection, read_ledger_query)
        print(type(current_year_ledger))
        print(f"read the ledger: {current_year_ledger}")
        if type(current_year_ledger) == str:
            current_year_ledger = False
        read_accounts_query = f"""SELECT * from tbl_Accounts WHERE Account_ID LIKE '{acct_types}%';"""
        accounts = db.execute_read_query_dict(icb_session.connection, read_accounts_query)
        #print(accounts)
        #Create and display the chart of accounts.
        chart_of_accounts_display_content = []
        for account in accounts:
            account_type = 1
            account_Id = str(account['Account_ID'])
            account_Name = str(account['Name'])
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
                    if debit_account == account_Id:
                        debits = debits + amount
                        balance = account_type*(debits - credits)
                    elif credit_account == account_Id:
                        credits = credits + amount
                        balance = account_type*(debits - credits)
            credits =  format_currency(credits)
            debits = format_currency(debits)
                
            balance = format_currency(balance)
            
            chart_of_accounts_display_content.append([account_Id,account_Name,credits, debits, balance])
        window['-Chart_of_Accounts_Content-'].update(chart_of_accounts_display_content)        


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
        elif event == "-Account_Type_Picker-":
            if values["-Account_Type_Picker-"] == "All Accounts":
                update_chart_of_accounts(icb_session.window, values, "All Accounts")
            else:
                update_chart_of_accounts(icb_session.window, values, values["-Account_Type_Picker-"][:2])


            
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
                print("this_layout")
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
                print("while loop starting")
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
                        print("icb_session.transaction_date")
                        print(icb_session.transaction_date)
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
                        add_transaction_to_database(values)
                        icb_session.transaction = load_ledger_tab(icb_session.window,values)
                        new_transaction_window.close()

                #new_transaction_window.close()

            #print(values)
        elif event == "-Ledger_Display_Content-":
            ledger_content = values['-Ledger_Display_Content-']
            print(ledger_content)
            if len(ledger_content) != 0:
                this_transaction_index = ledger_content[0]
                this_transaction = icb_session.transactions[this_transaction_index][0]
                load_transaction_details(this_transaction)
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
                vendor_number_query = f"""SELECT MAX(Vendor_ID) FROM tbl_Vendors;"""
                new_vendor_number = db.execute_read_query(icb_session.connection,vendor_number_query)
                print(icb_session.vendor_number)
                print(new_vendor_number[0][0])
                if type(new_vendor_number[0][0]) !=int:
                    icb_session.vendor_number = int(0)
                else:
                    icb_session.vendor_number = new_vendor_number[0][0] + 1
                this_layout, icb_session.num = new_vendor_layout(icb_session.num,icb_session.vendor_number)
                #print(this_layout, icb_session.num)
                new_vendor_window = sg.Window(title="Add a Vendor", location=(900,200),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
                new_vendor_window.close_destroys_window = True
                event_newv, values_newv = new_vendor_window.read(close=True)
                values.update(values_newv)      
                if event_newv == f"-Submit_Vendor_Button_{icb_session.num}-":
                    print(f"""Adding {values[f'-Vendor_Name_{icb_session.num}-']}""")
                    add_vendor_to_database(icb_session.window,values)
        elif event=="-View_Vendors_Content-":
            print(event)
            this_index = values["-View_Vendors_Content-"]     
            print(this_index)
            if len(this_index) > 0:
                load_single_vendor(icb_session.window, values, icb_session.vendors[this_index[0]])          
        elif event == "View Customers":
            this_tab_index = 4
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
        elif event == "-New_Customer_Button-":
                customer_number_query = f"""SELECT MAX(Customer_ID) FROM tbl_Customers;"""
                new_customer_number = db.execute_read_query(icb_session.connection,customer_number_query)
                #print(icb_session.customer_number)
                #print(new_customer_number[0][0])
                
                if type(new_customer_number[0][0]) != int:
                    icb_session.customer_number = int(0)
                else:
                    icb_session.customer_number = new_customer_number[0][0] + 1
                this_layout, icb_session.num = new_customer_layout(icb_session.num,icb_session.customer_number)
                #print(this_layout, icb_session.num)
                new_customer_window = sg.Window(title="Add a Customer", location=(900,200),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
                new_customer_window.close_destroys_window = True
                event_newc, values_newc = new_customer_window.read(close=True)
                values.update(values_newc)      
                if event_newc == f"-Submit_Customer_Button_{icb_session.num}-":
                    print(f"""Adding {values[f'-Customer_Name_{icb_session.num}-']}""")
                    add_customer_to_database(icb_session.window,values)            

        elif event == "Invoicing" or event == 'Sell Inventory':
            this_tab_index = 5
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
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
            icb_session.connection = False
            this_layout, icb_session.num = new_database_layout(icb_session.num)
            #print(this_layout, icb_session.num)
            new_database_window = sg.Window(title="Create a New Database", location=(900,500),layout= this_layout, margins=(10,10), resizable=True, size=(480,500))
            new_database_window.close_destroys_window = True
            event_newdb, values_newdb = new_database_window.read(close=True)
            values.update(values_newdb)
            if event_newdb == "Exit Iceberg" or event == sg.WIN_CLOSED:
                icb_session.guitimer = "Initializing"
            elif event_newdb == f"-Submit_New_Database_Button_{icb_session.num}-": 
                icb_session.filekey, icb_session.filename,  chart_of_accounts_display_content = create_database(values, icb_session.current_console_messages, icb_session.window, icb_session.num, current_year)
                #print(ledger_name)
                icb_session.current_console_messages = icb_session.console_log(f"Database created: {icb_session.db_name}", icb_session.current_console_messages)
                icb_session.current_console_messages = icb_session.console_log(f"Filekey created: {icb_session.filename}", icb_session.current_console_messages)
                icb_session.current_console_messages = icb_session.console_log("Dashboard statistics updated.", icb_session.current_console_messages)
                icb_session.guitimer = "Initializing"
        elif event == "Open Database":    
            icb_session.connection = False
            this_layout, icb_session.num = open_database_layout(icb_session.num)
            #print(this_layout, icb_session.num)
            new_database_window = sg.Window(title="Open a Database", location=(900,500),layout= this_layout, margins=(10,10), resizable=True, size=(480,120))
            event_opendb, values_opendb = new_database_window.read(close=True)
            values.update(values_opendb)
            if event_opendb == f"-Open_Database_Button_{icb_session.num}-": 
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
                


                #Multiple yearly ledgers model (obsolete)

                #get_ledgers_query = f"""SELECT Property_Value FROM tbl_Properties WHERE Property_Name IS 'Ledgers';"""
                #these_ledgers = db.execute_read_query_dict(icb_session.connection,get_ledgers_query)
                #for ledger in these_ledgers:

                #print(f"these_ledgers: {these_ledgers}")
                #ledger_list = list(eval(these_ledgers[0]["Property_Value"]))
                #print(f"ledger_list: {ledger_list}")
                #New year check:
                #if ledger_list[-1] != ledger_list[0][:-4] + f"{icb_session.current_year}":
                #    #ledger_name_1 = f"""ledger_{icb_session.ledger_name[:-4]}"""
                #    this_ledger = f"{icb_session.current_year}"""
                    

                #    ledger_list.append(this_ledger)

                #    #Insert the new ledger table into the database
                #    ledgers_update_query = f"""UPDATE tbl_Properties SET Property_Value = '{ledger_list}';"""
                #icb_session.window['-Year_Picker-'].update(values=ledger_list)
                #icb_session.ledger_tables = ledger_list
                #print(icb_session.ledger_name)
                
                get_ledgers_query = f"""SELECT Property_Value FROM tbl_Properties WHERE Property_Name IS 'Ledger Name';"""
                this_ledger = db.execute_read_query_dict(icb_session.connection,get_ledgers_query)
                print(this_ledger)
                icb_session.ledger_name = this_ledger[0]['Property_Value']
                #Log to console
                icb_session.current_console_messages = icb_session.console_log(f"Filekey Read: {icb_session.filename}", icb_session.current_console_messages)
                icb_session.current_console_messages = icb_session.console_log(f"Database Opened: {icb_session.db_name}", icb_session.current_console_messages)
                icb_session.current_console_messages = icb_session.console_log("Dashboard statistics updated.", icb_session.current_console_messages)
                

                #Switch to the dashboard and update statistics
                this_tab_index = 0
                for i in range(len(tab_keys)):
                    if i == this_tab_index:
                        icb_session.window[tab_keys[i]].update(visible=True)
                        icb_session.window[tab_keys[i]].select()
                    else:
                        icb_session.window[tab_keys[i]].update(visible=False)                
                
                
                
                icb_session.window, chart_of_accounts_display_content = update_dashboard_statistics(icb_session.window, values)


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
            
        elif event == "-View_Account_Button-" or event == "-Chart_of_Accounts_Content-":
            account_index = values["-Chart_of_Accounts_Content-"]
            print(account_index[0])
            print(chart_of_accounts_display_content)
            account_number = chart_of_accounts_display_content[account_index[0]][0]
            this_tab_index = 8
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            icb_session.window, values = load_view_account_tab(icb_session.window, values, account_number, icb_session.ledger_name)
        elif event == "Database Properties":
            this_tab_index = 9
            for i in range(len(tab_keys)):
                if i == this_tab_index:
                    icb_session.window[tab_keys[i]].update(visible=True)
                    icb_session.window[tab_keys[i]].select()
                else:
                    icb_session.window[tab_keys[i]].update(visible=False)
            load_database_properties_tab(icb_session.window, values, icb_session.connection)
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
            this_layout, icb_session.num = new_account_layout(icb_session.num)
            new_account_window = sg.Window(title="Open a Database", location=(900,500),layout= this_layout, margins=(10,10), resizable=True, size=(480,600))
            
            while True:
                event_newacc, values_newacc = new_account_window.read(close=False)
                if values_newacc != None:
                    values.update(values_newacc)
                if event_newacc == sg.WIN_CLOSED:
                    break
                elif event_newacc == f"-Account_Type_Picker_{icb_session.num}-":
                    pass
                elif event_newacc == f"-Submit_Account_Button_{icb_session.num}-":        
                    added_account = add_account_to_database(values)     
                    icb_session.current_console_messages = icb_session.console_log(f"New Account Created: {added_account}",icb_session.current_console_messages)
                    new_account_window.close()
                    update_dashboard_statistics(icb_session.window,values)
        #elif event == f"-Business_Receipts_Repository_{num}-":
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
            
        


icb_session.window.close()
