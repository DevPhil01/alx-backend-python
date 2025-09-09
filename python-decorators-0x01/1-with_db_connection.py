import sqlite3
import functools

def with_db_connection(func):
    """Decorator to open and close database connection automatically."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass connection to the wrapped function
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Ensure connection is always closed
            conn.close()
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

#### Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)
