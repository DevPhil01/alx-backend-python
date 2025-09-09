import time
import sqlite3 
import functools

# Dictionary to store cached query results
query_cache = {}

def with_db_connection(func):
    """
    Decorator to handle database connection.
    Opens a connection, passes it to the function, and closes it afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

def cache_query(func):
    """
    Decorator to cache query results based on the SQL query string.
    If the query has been executed before, returns the cached result instead of querying the database.
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print(f"Fetching from cache for query: {query}")
            return query_cache[query]
        print(f"Executing and caching query: {query}")
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will execute the query and cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")
print("First call:", users)

# Second call will fetch the result from cache
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print("Second call:", users_again)
