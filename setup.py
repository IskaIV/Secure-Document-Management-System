import sqlite3


def start_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create valid WorkID table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ValidWorkID (
            WORKID TEXT PRIMARY KEY,
        )
    ''')

    # Create the User table
    # Use WORKID from ValidWorkID as the primary key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            WORKID TEXT PRIMARY KEY,
            First TEXT,
            Last TEXT,
            Password TEXT
        )
    ''')

    # Create the Login table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Login (
            WORKID TEXT,
            Password TEXT,
            First TEXT,
            Last TEXT
        )
    ''')

    # Create the Files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Files (
            FileId INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName TEXT,
            FileData BLOB
        )
    ''')


    with open('workers.txt', 'r') as file:
        for line in file:
            worker_id = line.strip()
            if worker_id:
                query = "INSERT INTO ValidWorkID (WORKID) VALUES (?)"
                cursor.execute(query, (worker_id,))

    cursor.close()
