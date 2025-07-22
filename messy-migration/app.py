# app.py
from flask import Flask, request, jsonify, g # Import 'g' for request-scoped globals
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re # For email validation
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)

# --- Configuration ---
# Use environment variables for sensitive data and configuration in production
# For this challenge, we'll use defaults or simple checks.
DATABASE = 'users.db'
# IMPORTANT: In a real application, SECRET_KEY should be a long, random string
# loaded securely from environment variables or a configuration management system.
SECRET_KEY = os.environ.get('SECRET_KEY', 'your_super_secret_key_change_me_in_prod_env') 
DEBUG_MODE = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG_MODE

# --- Database Connection Management (Flask Best Practice) ---
def get_db():
    """
    Establishes a request-scoped connection to the SQLite database.
    The connection is stored on Flask's 'g' object and will be closed
    automatically at the end of the request.
    """
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row # This allows accessing columns by name
            # Enable foreign key support (important for referential integrity)
            g.db.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            app_logger.critical(f"Database connection error: {e}")
            # In a real app, you might want to return a 500 or handle more gracefully
            raise # Re-raise to be caught by a higher-level error handler
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database connection at the end of the application context."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        app_logger.debug("Database connection closed.")

def init_db_schema():
    """Initializes the database schema if the table does not exist.
    This function is called once on application startup within the app context.
    """
    conn = None # Initialize conn to None for finally block
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute("PRAGMA foreign_keys = ON;") # Ensure foreign keys are ON for schema creation
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE, -- Email should be unique for user accounts
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        app_logger.info("Database schema initialized successfully.")
    except sqlite3.Error as e:
        app_logger.critical(f"FATAL: Error initializing database schema: {e}")
        # In a real app, you might want to exit if DB cannot be initialized
    finally:
        if conn:
            conn.close()

# Initialize DB schema on app startup.
# This is typically done via a separate script (like init_db.py) or a CLI command.
# For a small app/challenge, doing it on first request/app context can work.
with app.app_context():
    init_db_schema()

# --- Utility Functions ---
def validate_email(email):
    """
    Performs basic email format validation.
    
    Args:
        email (str): The email string to validate.
        
    Returns:
        bool: True if the email format is valid, False otherwise.
    """
    # More robust regex for email validation
    # This regex covers common email patterns, but for strict RFC compliance,
    # consider a dedicated library like 'email_validator'.
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email)

def validate_password_strength(password):
    """
    Performs basic password strength validation (e.g., minimum length).
    
    Args:
        password (str): The password string to validate.
        
    Returns:
        bool: True if the password meets strength requirements, False otherwise.
    """
    MIN_PASSWORD_LENGTH = 8
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
    # Add more complexity checks here (e.g., requires uppercase, lowercase, digit, special char)
    # e.g., if not re.search(r"[A-Z]", password): return False, "Password needs uppercase"
    return True, ""

# --- Error Handlers ---
# These handlers ensure consistent JSON error responses for common HTTP errors.

@app.errorhandler(400)
def bad_request(error):
    app_logger.warning(f"Bad request: {request.url} - {error.description}")
    return jsonify({"error": "Bad Request", "message": error.description}), 400

@app.errorhandler(404)
def not_found(error):
    app_logger.warning(f"Not Found: {request.url} - {error.description}")
    return jsonify({"error": "Not Found", "message": error.description}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    app_logger.warning(f"Method Not Allowed: {request.method} {request.url}")
    return jsonify({"error": "Method Not Allowed", "message": error.description}), 405

@app.errorhandler(500)
def internal_server_error(error):
    # Log the full traceback for internal server errors
    app_logger.exception("An internal server error occurred") 
    return jsonify({"error": "Internal Server Error", "message": "Something went wrong on the server."}), 500

# --- Routes ---

@app.route('/')
def home():
    """
    Health check endpoint for the API.
    
    Returns:
        Flask.Response: JSON response indicating API status.
    """
    return jsonify({"message": "User Management System API is running!"}), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    """
    Retrieve a list of all users, excluding sensitive information like password hashes.
    
    Returns:
        Flask.Response: JSON array of user objects.
    """
    try:
        db = get_db()
        # Select only necessary fields (id, name, email) to avoid exposing password hash
        users_data = db.execute("SELECT id, name, email FROM users").fetchall()
        # Convert list of sqlite3.Row objects to list of dictionaries for JSON serialization
        users_list = [dict(user) for user in users_data]
        return jsonify({"users": users_list}), 200
    except Exception as e:
        app_logger.error(f"Error retrieving all users: {e}")
        return jsonify({"error": "Failed to retrieve users", "details": str(e)}), 500

@app.route('/user/<int:user_id>', methods=['GET']) # Using int: for automatic type conversion and validation
def get_user(user_id):
    """
    Retrieve a specific user by their ID.
    
    Args:
        user_id (int): The ID of the user to retrieve.
        
    Returns:
        Flask.Response: JSON object of the user if found, or 404 error.
    """
    try:
        db = get_db()
        # Use parameterized query to prevent SQL injection
        user = db.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
        
        if user:
            return jsonify({"user": dict(user)}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        app_logger.error(f"Error retrieving user with ID {user_id}: {e}")
        return jsonify({"error": "Failed to retrieve user", "details": str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user with provided name, email, and password.
    Password is hashed before storage.
    
    Returns:
        Flask.Response: JSON response with success message and new user ID, or error.
    """
    # Use request.get_json() which correctly handles content-type and parsing
    data = request.get_json() 

    if not data:
        return jsonify({"error": "Invalid JSON", "message": "Request body must be valid JSON."}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Input validation for required fields
    if not name or not email or not password:
        return jsonify({"error": "Missing Data", "message": "Name, email, and password are required."}), 400
    
    # Validate email format
    if not validate_email(email):
        return jsonify({"error": "Invalid Email", "message": "Please provide a valid email address."}), 400

    # Validate password strength
    is_password_strong, password_msg = validate_password_strength(password)
    if not is_password_strong:
        return jsonify({"error": "Weak Password", "message": password_msg}), 400

    # Hash the password before storing it in the database
    hashed_password = generate_password_hash(password)

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       (name, email, hashed_password)) # Parameterized query
        db.commit()
        app_logger.info(f"User created: {email}, ID: {cursor.lastrowid}")
        return jsonify({"message": "User created successfully!", "id": cursor.lastrowid}), 201 # 201 Created
    except sqlite3.IntegrityError: # Specific error for unique constraint violation (e.g., email already exists)
        db.rollback() # Rollback the transaction on error
        app_logger.warning(f"Attempted to create user with existing email: {email}")
        return jsonify({"error": "Conflict", "message": "User with this email already exists."}), 409
    except sqlite3.Error as e:
        db.rollback() # Rollback on any other DB error
        app_logger.error(f"Database error creating user: {e}", exc_info=True)
        return jsonify({"error": "Database Error", "message": "Failed to create user."}), 500

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update an existing user's name and/or email by ID.
    
    Args:
        user_id (int): The ID of the user to update.
        
    Returns:
        Flask.Response: JSON response with success message or error.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON", "message": "Request body must be valid JSON."}), 400

    name = data.get('name')
    email = data.get('email')
    
    # At least one field should be provided for update
    if not name and not email:
        return jsonify({"error": "No Data", "message": "At least 'name' or 'email' must be provided for update."}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        # Check if user exists first to return 404 if not found
        user_exists = cursor.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user_exists:
            return jsonify({"message": "User not found"}), 404

        update_fields = []
        params = []
        
        if name:
            update_fields.append("name = ?")
            params.append(name)
        if email:
            if not validate_email(email):
                return jsonify({"error": "Invalid Email", "message": "Please provide a valid email address."}), 400
            update_fields.append("email = ?")
            params.append(email)

        # This case should ideally be caught by the earlier `if not name and not email:`
        if not update_fields: 
            return jsonify({"error": "No Valid Fields", "message": "No valid fields to update."}), 400

        params.append(user_id) # Add user_id to the end of parameters for the WHERE clause
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, tuple(params)) # Parameterized query
        db.commit()

        # Check if any rows were actually affected by the update (e.g., if user_id was valid)
        if cursor.rowcount == 0: 
            # This case means the user was found, but no effective changes were made (e.g., updating with same data)
            app_logger.info(f"User {user_id} update requested, but no changes were made.")
            return jsonify({"message": "User found, but no changes were applied (data was identical or no valid fields provided)."}), 200 
        
        app_logger.info(f"User {user_id} updated.")
        return jsonify({"message": "User updated successfully!"}), 200
    except sqlite3.IntegrityError: # Handle unique email constraint violation
        db.rollback()
        app_logger.warning(f"Attempted to update user {user_id} with existing email: {email}")
        return jsonify({"error": "Conflict", "message": "Email already in use by another user."}), 409
    except sqlite3.Error as e:
        db.rollback()
        app_logger.error(f"Database error updating user {user_id}: {e}", exc_info=True)
        return jsonify({"error": "Database Error", "message": "Failed to update user."}), 500

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user by their ID.
    
    Args:
        user_id (int): The ID of the user to delete.
        
    Returns:
        Flask.Response: Empty response with 204 status if successful, or error.
    """
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,)) # Parameterized query
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "User not found"}), 404
        else:
            app_logger.info(f"User {user_id} deleted.")
            return '', 204 # 204 No Content should have an empty body
    except sqlite3.Error as e:
        db.rollback()
        app_logger.error(f"Database error deleting user {user_id}: {e}", exc_info=True)
        return jsonify({"error": "Database Error", "message": "Failed to delete user."}), 500

@app.route('/search', methods=['GET'])
def search_users():
    """
    Search users by name (case-insensitive, partial match).
    
    Query Parameters:
        name (str): The name or partial name to search for.
        
    Returns:
        Flask.Response: JSON array of matching user objects.
    """
    name_query = request.args.get('name')

    if not name_query:
        return jsonify({"error": "Missing Parameter", "message": "Please provide a 'name' query parameter to search."}), 400
    
    # Use LIKE with wildcards for partial search.
    # Convert query to lowercase for case-insensitive search if DB's LIKE is case-sensitive.
    # SQLite's LIKE is case-insensitive for ASCII by default, but explicit lower() can be safer for non-ASCII.
    search_pattern = f"%{name_query}%" 

    try:
        db = get_db()
        users_data = db.execute("SELECT id, name, email FROM users WHERE name LIKE ?", (search_pattern,)).fetchall()
        users_list = [dict(user) for user in users_data]
        app_logger.info(f"Search for '{name_query}' returned {len(users_list)} results.")
        return jsonify({"users": users_list}), 200
    except Exception as e:
        app_logger.error(f"Error searching users with query '{name_query}': {e}", exc_info=True)
        return jsonify({"error": "Failed to search users", "details": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """
    User login endpoint. Checks provided email and password against stored hashed password.
    
    Returns:
        Flask.Response: JSON response indicating success/failure and user ID if successful.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON", "message": "Request body must be valid JSON."}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing Credentials", "message": "Email and password are required."}), 400

    try:
        db = get_db()
        # Fetch only the password hash and ID for verification
        user = db.execute("SELECT id, password FROM users WHERE email = ?", (email,)).fetchone()

        # Check if user exists and verify the hashed password
        if user and check_password_hash(user['password'], password):
            app_logger.info(f"Login successful for user ID: {user['id']}")
            return jsonify({"status": "success", "message": "Login successful!", "user_id": user['id']}), 200
        else:
            app_logger.warning(f"Failed login attempt for email: {email}")
            # Do not specify if email or password was wrong for security reasons
            return jsonify({"status": "failed", "message": "Invalid email or password."}), 401 # 401 Unauthorized
    except Exception as e:
        app_logger.error(f"Error during login for email {email}: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": "An error occurred during login."}), 500


if __name__ == '__main__':
    # In a production deployment, use a WSGI server like Gunicorn or uWSGI.
    # The 'host' and 'port' here are for local development as per challenge.
    # Debug mode is now configured via FLASK_DEBUG environment variable.
    app_logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000)