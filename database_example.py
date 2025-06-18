import sqlite3
from tabulate import tabulate

def view_table(table_name):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    # Fetch all rows from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Fetch table headers
    cursor.execute(f"PRAGMA table_info({table_name})")
    headers = [header[1] for header in cursor.fetchall()]

    # Print table in tabular format
    print(tabulate(rows, headers=headers, tablefmt='grid'))

    conn.close()

if __name__ == "__main__":
    table_name = "my_table"  # Replace with your actual table name
    view_table(table_name)