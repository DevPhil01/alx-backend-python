import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator to automatically open and close a database connection.
    """
    @functools.wraps(func)
    def wrapper_with_db_connection(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper_with_db_connection

def transactional(func):
    """
    Decorator to wrap database operations inside a transaction.
    Commits if successful, rolls back if an error occurs.
    """
    @functools.wraps(func)
    def wrapper_transactional(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # Commit if no errors
            return result
        except Exception as e:
            conn.rollback()  # Rollback if there is an error
            print(f"Transaction failed: {e}")
            raise
    return wrapper_transactional

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    print(f"Updated email for user {user_id} to {new_email}")

# Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
