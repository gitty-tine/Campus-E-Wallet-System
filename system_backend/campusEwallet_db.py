import mysql.connector
from mysql.connector import Error


def connect_to_db():
    """
    Establish a connection to the MySQL database.

    This function attempts to connect to the MySQL database using
    the provided connection credentials.

    Returns:
        mysql.connector.connection.MySQLConnection | None:
            A database connection object if successful,
            otherwise None if the connection fails.
    """
    try:
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="campusewallet_db"
        )

        if database.is_connected():
            return database
    
    except Error as e:
        print(f"An error occured while connecting to the database: {e}")
        return None


def execute_query(query, parameters=None):
    """
    Execute an SQL query that modifies the database.

    This function is typically used for INSERT, UPDATE,
    or DELETE queries. It commits the changes after execution.

    Args:
        query (str): The SQL query to be executed.
        parameters (tuple | None): Optional parameters for
            parameterized SQL queries.

    Returns:
        mysql.connector.cursor.MySQLCursor | None:
            The cursor object after execution,
            or None if an error occurs.
    """
    try:
        database = connect_to_db()
        if not database:
            return None
        
        cursor = database.cursor()
        cursor.execute(query, parameters)
        database.commit()

        return cursor
    
    except Error as e:
        print(f"An error occured while executing SQL query: {e}")
        return None


def fetch_one(query, parameters=None):
    """
    Retrieve a single record from the database.

    This function executes a SELECT query and returns
    the first matching row as a dictionary.

    Args:
        query (str): The SQL SELECT query to be executed.
        parameters (tuple | None): Optional parameters for
            parameterized SQL queries.

    Returns:
        dict | None:
            A dictionary representing one database record,
            or None if no record is found or an error occurs.
    """
    try:
        database = connect_to_db()
        if not database:
            return None
        
        cursor = database.cursor(dictionary=True)
        cursor.execute(query, parameters)

        return cursor.fetchone()
    
    except Error as e:
        print(f"An error occured while retrieving data from the database: {e}")
        return None


def fetch_all(query, parameters=None):
    """
    Retrieve multiple records from the database.

    This function executes a SELECT query and returns
    all matching rows as a list of dictionaries.

    Args:
        query (str): The SQL SELECT query to be executed.
        parameters (tuple | None): Optional parameters for
            parameterized SQL queries.

    Returns:
        list[dict] | None:
            A list of dictionaries containing database records,
            or None if an error occurs.
    """
    try:
        database = connect_to_db()
        if not database:
            return None
        
        cursor = database.cursor(dictionary=True)
        cursor.execute(query, parameters)

        return cursor.fetchall()
    
    except Error as e:
        print(f"An error occured while retrieving data from the database: {e}")
        return None