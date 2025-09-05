# PostgreSQL Database Seeder

This project provides a Python script (`seed.py`) to set up and populate a PostgreSQL database named **ALX_prodev** with a `user_data` table and sample user records.

---

## Features

- Creates a PostgreSQL database (`ALX_prodev`) if it does not exist.
- Creates a `user_data` table with the following fields:
  - `user_id`: UUID, Primary Key, Indexed
  - `name`: VARCHAR, NOT NULL
  - `email`: VARCHAR, NOT NULL
  - `age`: DECIMAL, NOT NULL
- Inserts sample user data provided in the script.
- Ensures no duplicate entries during insertion.

---

## Prerequisites

- **Python 3.x**
- **PostgreSQL** installed and running
- `psycopg2` library installed (`pip install psycopg2`)

---

## Usage Instructions

1. **Clone or download the project files.**

2. **Update PostgreSQL credentials** in `seed.py`:
   ```python
   connection = psycopg2.connect(
       dbname="postgres",
       user="your_username",
       password="your_password",
       host="localhost",
       port="5432"
   )
   ```

3. **Run the script**:
   ```bash
   python seed.py
   ```

4. **Verify the data**:
   ```sql
   \c ALX_prodev;
   SELECT * FROM user_data;
   ```

---

## Functions Overview

### `connect_db()`
Connects to the default PostgreSQL server (usually `postgres` database).

### `create_database(connection)`
Creates the database `ALX_prodev` if it does not already exist.

### `connect_to_prodev()`
Connects to the `ALX_prodev` database after it has been created.

### `create_table(connection)`
Creates the `user_data` table with the specified schema if it does not already exist.

### `insert_data(connection, data)`
Inserts sample user records into the database, skipping duplicates.

---

## Sample Data Inserted

- **Total Records**: 100+
- Includes randomly generated names, emails, and ages.
- Data is provided inline within the script.

---

## Notes

- Ensure PostgreSQL is running before executing the script.
- Modify host, port, username, and password as needed for your environment.
- The script uses UUIDs for primary keys to ensure uniqueness.

---
