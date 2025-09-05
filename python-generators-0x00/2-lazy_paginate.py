import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection settings
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
    :param offset: Starting row number for pagination.
    :return: List of users for the current page.
    """
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM user_data LIMIT %s OFFSET %s;",
                (page_size, offset)
            )
            return cursor.fetchall()
    finally:
        if connection:
            connection.close()

def lazy_paginate(page_size=50):
    """
    Generator to lazily load pages of users.
    Loads one page at a time using LIMIT and OFFSET.
    :param page_size: Number of users per page (default: 50)
    :yield: List of users in each page
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:  # Stop when no more data
            break
        yield page  # Yield the page to the caller
        offset += page_size

# Example usage
if __name__ == "__main__":
    print("Lazy pagination (page size = 50):")
    for page in lazy_paginate(50):
        print(f"Fetched {len(page)} users")
        for user in page:
            print(user)
