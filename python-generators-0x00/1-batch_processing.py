import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_CONFIG = {
    "dbname": "ALX_prodev",
    "user": "postgres",
    "password": "your_password",  # Replace with your PostgreSQL password
    "host": "localhost",
    "port": "5432"
}

def stream_users_in_batches(batch_size=50):
    """
    Generator to fetch users from the database in batches of specified size.
    :param batch_size: Number of rows per batch (default: 50)
    :yield: List of user records per batch
    """
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT COUNT(*) FROM user_data;")
            total_rows = cursor.fetchone()["count"]
            offset = 0

            # Loop through the table in batches
            while offset < total_rows:
                cursor.execute(
                    "SELECT * FROM user_data ORDER BY user_id LIMIT %s OFFSET %s;",
                    (batch_size, offset)
                )
                rows = cursor.fetchall()
                if not rows:
                    break
                yield rows  # Yield each batch instead of returning all
                offset += batch_size
    finally:
        if connection:
            connection.close()

def batch_processing(batch_size=50):
    """
    Generator to process batches of users and yield those over the age of 25.
    :param batch_size: Number of rows per batch (default: 50)
    :yield: Filtered user records (one by one)
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if float(user["age"]) > 25:  # Filtering condition
                yield user  # Yield one user at a time instead of returning all

# Example usage
if __name__ == "__main__":
    print("Streaming users over 25 years old:")
    for user in batch_processing(50):  # Batch size of 50
        print(user)
