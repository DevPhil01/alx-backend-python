import sqlite3

class ExecuteQuery:
    """
    Context manager to handle database connection and execute a given query.
    """
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params if params else ()
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """Open the connection, execute the query, and return the results."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results  # Makes the results accessible via 'as' in with-statement

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit if no exception, rollback if there is, and close the connection."""
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
            print(f"An error occurred: {exc_val}")
        self.cursor.close()
        self.conn.close()

# Usage example
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery('users.db', query, params) as results:
    print("Users older than 25:", results)
