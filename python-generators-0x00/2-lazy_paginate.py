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

def paginate_users(page_size, offset):
    """
    Fetch a single page of users from the database.
    :param page_size: Number of users per page.
    :param offset: Starting point for fetching users.
    :return: List of users in the page.
    """
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM user_data ORDER BY user_id LIMIT %s OFFSET %s;",
                (page_size, offset)
            )
            return cursor.fetchall()
    finally:
        if connection:
            connection.close()

def lazy_paginate(page_size=50):
    """
    Generator to lazily paginate through users table.
    Fetches the next page only when needed.
    :param page_size: Number of users per page (default: 50)
    :yield: List of users in each page
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page  # Yield one page at a time
        offset += page_size

# Example usage
if __name__ == "__main__":
    print("Lazy pagination example (page size = 50):")
    for page in lazy_paginate(50):  # Page size of 50
        print(f"Fetched {len(page)} users")
        for user in page:
            print(user)
