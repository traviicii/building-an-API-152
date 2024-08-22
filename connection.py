import mysql.connector
from mysql.connector import Error

# database connection parameters
db_name = 'ecom'
user = 'root'
password = ''
host = 'localhost' # localhost = 127.0.0.1

def connection():
    '''
    Creates a connection to our ecom database.
    '''
    try:
        # attempt to establish a conenction with my DB
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )

        if conn.is_connected():
            print("Successfully connected to the database!")
            return conn
        
    except Error as e:
        print(f"Error: {e}")
        return None