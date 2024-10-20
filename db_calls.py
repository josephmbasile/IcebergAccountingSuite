import sqlite3
from sqlite3 import Error
import os
from cryptography.fernet import Fernet

def create_connection(path):
    connection = None
    try:
        print(path)
        connection = sqlite3.connect(path)
    except Error as e:
        return(f"""An error occured: {e}""")

    return connection

def close_connection(connection):
    sqlite3.Connection.close(connection)



def create_tables(connection, query):
    """Write databse query."""
    #print(query)
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        success_message = f"""Query executed successfully"""
        #print(success_message)
        return success_message

    except Error as e:
        print(f"""Table Creation Error: {e}""")
        return e



def execute_query(connection, query):
    """Write databse query."""
    #print(query)
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        success_message = f"""Query executed successfully"""
        #print(success_message)
        return success_message

    except Error as e:
        print(f"""An error occured: {e}""")
        return e


def execute_read_query(connection, query):
    """Returns a list of tuples from the database."""
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"""An error occured: {e}""")

def execute_read_query_tuple(connection, query):
    """Returns a list of tuple objects from the database."""
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    results = None
    try:
        cursor.execute(query)
        results = tuple(zip(cursor.fetchall()))
        res_tuples = [
            result
            for result in results
            #dict(zip(result[i].keys(),result[i]))
        ]
        return res_tuples
    except Error as e:
        print(f"""An error occured: {e}""")


def execute_read_query_dict(connection, query):
    """Returns a list of dictionary objects from the database."""
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    results = None
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        res_dicts = [
            dict(zip(result.keys(),result))
            for result in results
            #dict(zip(result[i].keys(),result[i]))
        ]
        return res_dicts
    except Error as e:
        return (f"""An error occured: {e}""")

def load_db_to_memory(database):
    """Input unecrypted database connection. Returns database connection."""
    

    connection = sqlite3.connect(':memory:') # create a memory database
    print(f"Opening db: {database}")
    

    query = "".join(line for line in database.iterdump())

    # Dump old database in the new one. 
    connection.executescript(query)

    return connection

def save_db_from_memory(connection,db_name):
    """Input unecrypted database connection. Returns database connection."""
    os.remove(f'{db_name}')

    connection_new = sqlite3.connect(f'{db_name}') 
    print(f"Saving db: {connection_new}")
    

    query = "".join(line for line in connection.iterdump())

    # Dump old database in the new one. 
    connection_new.executescript(query)

    #connection = load_db_to_memory(connection_new)

    return connection_new, connection

"""int sqlite3_key(
   sqlite3 *db,        /* The connection from sqlite3_open() */
   const void *pKey,   /* The key */
   int nKey            /* Number of bytes in the key */
);

int sqlite3_rekey(
   sqlite *db,                    /* Database to be rekeyed */
   const void *pKey, int nKey     /* The new key */
);"""



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
    filename=False will generate a new filekey (excyption only).
    save_location=False will save to the Iceberg directory.
    Returns filekey, filename, savelocation"""
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
        unencrypted_db = fernet.decrypt(original_db)
        with open(f'./{db_name_2}','wb') as encrypted_file:
            encrypted_file.write(unencrypted_db)
        return filekey, filename, save_location
    else:
        return "Error: Mode not selected. (encrypt or decrypt)", "", ""
    

def open_database(filename, db_name, save_location):
    """Reads and connects to the database using the filekey."""
    print("open_database()")
    filekey=""
    connection = False
    print(f"{db_name}")
    if filename == False:
        return "Error: Please select filekey to continue."
    else:
        connection_1 = create_connection(f"./{db_name}")
        valid_table = execute_read_query(connection_1,f"""SELECT * FROM tbl_Accounts""")
        print(valid_table)
        if valid_table == None:
            filekey, filename, save_location = encrypt_database(db_name, "decrypt", filename, save_location, False)
            print(f"open_database: {db_name}")
            connection_0 = create_connection(f"./{db_name}")
            connection = load_db_to_memory(connection_0)
            connection_0.close()
            filekey, filename, save_location = encrypt_database(db_name, "encrypt", filename, save_location, False)
            print(connection_0)
            return connection, filekey
        else:
            connection = load_db_to_memory(connection_1)
            connection_1.close()
            filekey, filename, save_location = encrypt_database(db_name, "encrypt", filename, save_location, False)
            print(connection_1)
            return connection, filekey
        
            

    



def save_database(connection, db_name, filename, save_location):
    """Saves the database using the filekey."""
    #print("save_database()")
    #print(f"{db_name}")
    if filename == False:
        return "Error: Please select filekey to continue."
    else:
        #filekey, filename, save_location = encrypt_database(db_name, "decrypt", filename, save_location, "temp.db")
        #print(f"897 Db: {db_name}")
        #connection_0 = db.create_connection(f"./{db_name}")
        connection_0 = save_db_from_memory(connection,db_name)
        #print(connection_0)
        close_connection(connection_0[0])
        filekey, filename, save_location = encrypt_database(db_name, "encrypt", filename, save_location, db_name)
    return f"Database saved to ./{db_name}; Key saved to {save_location}{filename}", connection


db_name = "Basile_Kemp_House12.icb"
mode = "encrypt"
filename = "Basile_Kemp_House12.icbkey"
save_location = "/home/joe/Documents/01_PyCounting/"
#save_location = "/home/joe/Documents/00_488 E MAIN/00_Finance/"
#filekey, filename, save_location = encrypt_database(db_name, mode, filename, save_location, False)

#print(filekey)
#print(filename)
#print(save_location)