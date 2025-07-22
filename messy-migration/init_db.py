# init_db.py
import sqlite3
from werkzeug.security import generate_password_hash # Import for password hashing
import os

# Define the database path
DATABASE = 'users.db'

def init_db():
    """Initializes the users database with a table and sample hashed data."""
    # Remove existing db file for a clean start if it exists
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print(f"Removed existing database file: {DATABASE}")

    conn = sqlite3.connect(DATABASE)
    # Enable foreign key support for the connection used for schema creation
    conn.execute("PRAGMA foreign_keys = ON;") 
    cursor = conn.cursor()

    print("Creating users table...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, -- Ensure email is unique
            password TEXT NOT NULL
        )
    ''')
    print("Users table created.")

    print("Inserting sample users with hashed passwords...")
    # Hash passwords before inserting sample data
    hashed_password_john = generate_password_hash('password123')
    hashed_password_jane = generate_password_hash('secret456')
    hashed_password_bob = generate_password_hash('qwerty789')
    hashed_password_diana = generate_password_hash('securepass')
    hashed_password_eve = generate_password_hash('evepassword')

    sample_users = [
        ('John Doe', 'john@example.com', hashed_password_john),
        ('Jane Smith', 'jane@example.com', hashed_password_jane),
        ('Bob Johnson', 'bob@example.com', hashed_password_bob),
        ('Diana Prince', 'diana@example.com', hashed_password_diana),
        ('Eve Adams', 'eve@example.com', hashed_password_eve)
    ]

    cursor.executemany(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        sample_users
    )
    
    conn.commit()
    conn.close()
    print("Database initialized with sample data (passwords hashed).")

if __name__ == '__main__':
    init_db()