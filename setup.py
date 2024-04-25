import sqlite3


def start_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create valid WorkID table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ValidWorkID (
            WORKID TEXT PRIMARY KEY
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

    # Create the Files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Files (
            FileId INTEGER PRIMARY KEY AUTOINCREMENT,
            FileName TEXT,
            FileData BLOB
        )
    ''')

    cursor.close()
