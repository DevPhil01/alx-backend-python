import psycopg2
from psycopg2.extras import RealDictCursor

def connect_to_prodev():
    """
    Connect to the ALX_prodev PostgreSQL database.
    Returns:
        connection: A connection object to the database.
    """
    try:
        connection = psycopg2.connect(
            dbname="ALX_prodev",
            user="your_username",
            password="your_password",
            host="localhost",
            port="5432"
        )
        return connection
    except Exception as e:
        print("Database connection failed:", e)
        return None

def stream_users():
    """
    Generator function to stream rows from user_data table one by one.

    Yields:
        dict: A dictionary containing a single row from the user_data table.
    """
    connection = connect_to_prodev()
    if not connection:
        return

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM user_data;")
            for row in cursor:
                yield row
    except Exception as e:
        print("Error streaming users:", e)
    finally:
        connection.close()

if __name__ == "__main__":
    # Example usage: stream and print each user row
    for user in stream_users():
        print(user)
