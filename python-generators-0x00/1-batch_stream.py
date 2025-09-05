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
    Generator to fetch rows from the user_data table in batches of size 50 by default.
    
    :param batch_size: Number of records to fetch per batch (default: 50)
    :yield: List of user records (dictionaries)
    """
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        offset = 0

        while True:
            # Fetch batch of users (default: 50)
            cursor.execute(
                "SELECT * FROM user_data ORDER BY user_id LIMIT %s OFFSET %s;",
                (batch_size, offset)
            )
            batch = cursor.fetchall()
            if not batch:
                break
            yield batch
            offset += batch_size
    finally:
        if connection:
            connection.close()

def batch_processing(batch_size=50):
    """
    Processes each batch of users (default: 50 per batch) and yields only those over the age of 25.
    
    :param batch_size: Number of records to fetch per batch (default: 50)
    :yield: Filtered user records
    """
    for batch in stream_users_in_batches(batch_size):
        # Filter users older than 25 from the current batch
        filtered_batch = [user for user in batch if float(user['age']) > 25]
        if filtered_batch:
            yield filtered_batch

# Example usage
if __name__ == "__main__":
    for batch in batch_processing():
        print("Filtered Batch (50 users per batch):")
        for user in batch:
            print(user)
