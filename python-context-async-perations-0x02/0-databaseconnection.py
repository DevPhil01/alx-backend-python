import sqlite3

class DatabaseConnection:
    """
    Custom context manager for handling database connections.
    Opens a connection on enter and closes it on exit.
    """
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """Open the database connection."""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the database connection, committing if no exception occurs."""
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
            print(f"An error occurred: {exc_val}")
        self.conn.close()

# Using the context manager to fetch users
with DatabaseConnection('users.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print("Query Results:", results)
