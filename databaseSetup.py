import mysql.connector
from mysql.connector import Error
import os

def create_database(cursor, database_name):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' created or already exists.")
    except Error as e:
        print(f"Failed to create database '{database_name}'. Error: {e}")

def create_table(cursor, table_query):
    try:
        cursor.execute(table_query)
        print("Table created successfully.")
    except Error as e:
        print(f"Failed to create table. Error: {e}")

def main():
    # Load environment variables
    os.getenv("load_dotenv()")

    # Database connection parameters
    host_name = "localhost"
    db_name = "discord_db"
    user_name = "discord"
    user_password = os.getenv('DISCORD_TOKEN')

    # SQL query to create a table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Date VARCHAR(255) NOT NULL,
        Card_Date VARCHAR(255),
        Title VARCHAR(255) NOT NULL,
        Title_Link VARCHAR(255),
        Event_Text VARCHAR(255),
        Event_Text_Link VARCHAR(255),
        Is_Virtual BOOLEAN DEFAULT FALSE,
        Price VARCHAR(255),
        Tags VARCHAR(255)
    )
    """

    # Create a database connection
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("USE {}".format(db_name))  # Select the database
            create_database(cursor, db_name)  # Create the database if it doesn't exist
            cursor.execute("USE {}".format(db_name))  # Re-select the database after creation
            create_table(cursor, create_table_query)  # Create the table
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    main()
