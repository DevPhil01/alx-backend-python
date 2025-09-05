import psycopg2

# Database connection details
DB_CONFIG = {
    "host": "localhost",
    "database": "ALX_prodev",
    "user": "postgres",
    "password": "your_password"  # Replace with your PostgreSQL password
}

def stream_user_ages():
    """
    Generator that streams user ages one by one from the user_data table.
    Yields:
        int: Age of a user.
    """
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data;")

        for row in cursor:
            yield row[0]

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def calculate_average_age():
    """
    Calculates the average age using the stream_user_ages generator without loading all data into memory.
    Prints:
        The average age of users.
    """
    total_age = 0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count > 0:
        average_age = total_age / count
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No user data found.")

if __name__ == "__main__":
    calculate_average_age()
