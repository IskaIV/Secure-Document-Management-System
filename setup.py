import sqlite3

def start_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create valid WorkID table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ValidWorkID (
            ROLE TEXT,
            WORKID TEXT PRIMARY KEY,
        )
    ''')

    # Create the User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            WORKID TEXT FOREIGN KEY,
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
        CREATE TABLE IF NOT EXISTS Posts (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            WORKID TEXT,
            Title TEXT,
            Description TEXT
        )
    ''')

    # Create the Replies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Replies (
            PrimaryUser TEXT,
            SecondaryUser TEXT,
            Message TEXT,
            Ind INTEGER PRIMARY KEY AUTOINCREMENT
        )
    ''')

    # Create the Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments (
            PostId INTEGER,
            CommentId INTEGER PRIMARY KEY AUTOINCREMENT,
            Content TEXT,
            Author TEXT
        )
    ''')
    cursor.close()
