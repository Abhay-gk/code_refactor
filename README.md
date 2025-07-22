✨ Refactored User Management API ✨

This repository hosts a refactored Python Flask API for managing user data, including creation, retrieval, updates, deletions, search, and login functionalities. Originally a legacy codebase with significant issues, this project has undergone a comprehensive refactoring process to enhance its security, maintainability, and adherence to modern best practices.

The goal was to transform a vulnerable and unorganized API into a robust, production-ready system, demonstrating a strong commitment to code quality and secure development.

🌟 Features
User Management:

Create new users (with secure password hashing).

Retrieve all users or a specific user by ID.

Update user details (name, email).

Delete users.

User Authentication:

Secure user login with hashed password verification.

Search Functionality:

Search users by name with partial and case-insensitive matching.

Robust Error Handling:

Consistent JSON error responses with appropriate HTTP status codes.

Data Integrity:

Ensures unique email addresses for user accounts.

Basic password strength validation.

✅ Refactoring Goals & Achievements
This refactoring initiative focused on addressing critical issues across several key areas:

🔒 Security Enhancements
SQL Injection Prevention: Migrated all database queries to use parameterized queries, completely eliminating the risk of SQL injection.

Secure Password Storage: Implemented werkzeug.security for hashing passwords before storage and securely verifying them during login, ensuring raw passwords are never exposed.

Email Uniqueness: Enforced a UNIQUE constraint on the email field at the database level and added API-level handling for 409 Conflict responses on duplicate email attempts.

Password Hash Protection: Modified user retrieval endpoints to explicitly exclude password hashes from responses.

🏗️ Code Organization & Maintainability
Request-Scoped Database Connections: Transitioned from a global database connection to a request-scoped connection pool managed by Flask's g object and teardown_appcontext, improving resource management and thread safety.

Clear Separation of Concerns: Decoupled database interaction logic, input parsing, and validation from core route handling, leading to cleaner, more modular, and reusable code.

Centralized Configuration: Introduced a dedicated configuration section for database path, secret key, and debug mode, supporting environment variable loading for production readiness.

💡 Best Practices Implementation
Consistent JSON API: Standardized all API responses to return structured JSON, including success messages and detailed error payloads.

Accurate HTTP Status Codes: Ensured every endpoint returns the semantically correct HTTP status code (e.g., 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 404 Not Found, 409 Conflict, 500 Internal Server Error).

Comprehensive Input Validation: Implemented checks for missing required fields, validated email formats, and added basic password strength validation.

Robust Error Handling: Integrated try-except blocks for database operations and JSON parsing, along with Flask's @app.errorhandler() decorators for consistent error responses.

Enhanced Logging: Configured basic application logging to provide better visibility into API operations and errors.

Production-Ready Setup: Removed debug=True from app.run and emphasized the use of WSGI servers for production deployments.

⚙️ Setup and Running
Follow these steps to get the API running locally:

Clone the repository:

git clone <your-repository-link>
cd messy-migration

Install dependencies:

pip install -r requirements.txt

Initialize the database:
This script creates the users.db SQLite database and populates it with sample users (with hashed passwords).

python init_db.py

Start the application:

python app.py

The API will be available at http://localhost:5000.

🔬 API Endpoints
The API provides the following endpoints, designed for clarity and ease of use:

GET / - Health Check
Description: Checks if the API is running and responsive.

Method: GET

Example Request:

curl http://localhost:5000/

Success Response (200 OK):

{
  "message": "User Management System API is running!"
}

GET /users - Get All Users
Description: Retrieves a list of all registered users, excluding sensitive information.

Method: GET

Example Request:

curl http://localhost:5000/users

Success Response (200 OK):

{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  ]
}

Error Response (500 Internal Server Error):

{
  "error": "Failed to retrieve users",
  "details": "..."
}

GET /user/<id> - Get Specific User
Description: Retrieves details for a single user by their unique ID.

Method: GET

Path Parameter: <id> (integer) - The ID of the user.

Example Request:

curl http://localhost:5000/user/1

Success Response (200 OK):

{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}

Error Response (404 Not Found):

{
  "message": "User not found"
}

POST /users - Create New User
Description: Registers a new user with a name, email, and password. The password is securely hashed before storage.

Method: POST

Example Request Body:

{
  "name": "Alice Wonderland",
  "email": "alice@example.com",
  "password": "StrongPassword123!"
}

Example Request (using curl):

curl -X POST -H "Content-Type: application/json" -d '{
    "name": "Alice Wonderland",
    "email": "alice@example.com",
    "password": "StrongPassword123!"
}' http://localhost:5000/users

Success Response (201 Created):

{
  "message": "User created successfully!",
  "id": 6
}

Error Responses (400 Bad Request, 409 Conflict):

{
  "error": "Missing Data",
  "message": "Name, email, and password are required."
}

{
  "error": "Invalid Email",
  "message": "Please provide a valid email address."
}

{
  "error": "Weak Password",
  "message": "Password must be at least 8 characters long."
}

{
  "error": "Conflict",
  "message": "User with this email already exists."
}

PUT /user/<id> - Update User
Description: Updates the name and/or email of an existing user.

Method: PUT

Path Parameter: <id> (integer) - The ID of the user to update.

Example Request Body (update name and email):

{
  "name": "Johnathan Doe",
  "email": "john.doe.new@example.com"
}

Example Request (using curl):

curl -X PUT -H "Content-Type: application/json" -d '{
    "name": "Johnathan Doe",
    "email": "john.doe.new@example.com"
}' http://localhost:5000/user/1

Success Response (200 OK):

{
  "message": "User updated successfully!"
}

Error Responses (400 Bad Request, 404 Not Found, 409 Conflict):

{
  "error": "No Data",
  "message": "At least 'name' or 'email' must be provided for update."
}

{
  "message": "User not found"
}

{
  "error": "Conflict",
  "message": "Email already in use by another user."
}

DELETE /user/<id> - Delete User
Description: Deletes a user from the system by their ID.

Method: DELETE

Path Parameter: <id> (integer) - The ID of the user to delete.

Example Request:

curl -X DELETE http://localhost:5000/user/2

Success Response (204 No Content):
(No response body, only status code)

Error Response (404 Not Found):

{
  "message": "User not found"
}

GET /search?name=<name> - Search Users by Name
Description: Searches for users whose names partially match the provided query, case-insensitively.

Method: GET

Query Parameter: name (string) - The name or partial name to search for.

Example Request:

curl "http://localhost:5000/search?name=john"

Success Response (200 OK):

{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  ]
}

Error Response (400 Bad Request):

{
  "error": "Missing Parameter",
  "message": "Please provide a 'name' query parameter to search."
}

POST /login - User Login
Description: Authenticates a user with their email and password.

Method: POST

Example Request Body:

{
  "email": "john@example.com",
  "password": "password123"
}

Example Request (using curl):

curl -X POST -H "Content-Type: application/json" -d '{
    "email": "john@example.com",
    "password": "password123"
}' http://localhost:5000/login

Success Response (200 OK):

{
  "status": "success",
  "message": "Login successful!",
  "user_id": 1
}

Error Response (401 Unauthorized, 400 Bad Request):

{
  "status": "failed",
  "message": "Invalid email or password."
}

{
  "error": "Missing Credentials",
  "message": "Email and password are required."
}

🧪 Testing the Application
A comprehensive test.py script is provided to verify the functionality and robustness of all API endpoints.

Ensure the Flask application is running (python app.py).

Ensure a clean database state by running python init_db.py before each test run.

Execute the test script:

python test.py

The script will print detailed output for each test, indicating success or failure, along with status codes and response bodies.

📈 Future Enhancements
With more time, the following improvements would further enhance the API:

Full Authentication & Authorization: Implement proper session management (e.g., Flask-Login) or token-based authentication (JWTs) to secure all endpoints requiring user context. Add role-based access control.

Advanced Input Validation: Integrate a dedicated validation library (e.g., Marshmallow, Pydantic) for more complex schema validation and clearer error messages.

Comprehensive Logging: Implement a structured logging setup to capture detailed application and request logs for monitoring and debugging in production.

Database Migrations: Utilize a tool like Alembic to manage database schema changes gracefully and version control the database schema.

Environment Configuration: Formalize environment-specific configurations (development, testing, production) using a pattern like Flask's config objects or python-dotenv.

Containerization (Docker): Dockerize the application for easier deployment and consistent environments.

More Extensive Automated Testing: Expand the test.py into a full pytest suite, including unit tests for helper functions and more exhaustive integration tests.

RESTful API Design Enhancements: Implement features like pagination, filtering, and sorting for GET /users and GET /search endpoints. Consider API versioning.

🛠️ Technologies Used
Python 3.x

Flask: Web framework

Werkzeug: Utilities for password hashing (dependency of Flask)

SQLite3: Database

🤖 AI Usage Policy
This solution was developed with the assistance of an AI assistant, specifically Gemini (a large language model by Google).

The AI was used for the following purposes:

Initial Code Analysis: To quickly identify major issues, security vulnerabilities, and areas for improvement in the provided legacy codebase.

Refactoring Strategy Development: To brainstorm and outline the most effective approaches for addressing identified issues, prioritizing security and best practices.

Code Generation: To generate the refactored Python code for app.py and init_db.py, incorporating the planned improvements (e.g., parameterized queries, password hashing, error handling, JSON responses, request-scoped database connections, and basic password strength validation).

Documentation Generation: To structure and articulate the CHANGES.md and this README.md document, including the identification of issues, justification for changes, assumptions, trade-offs, and future considerations.

The AI-generated code was directly utilized as it aligned with the identified best practices and addressed the core requirements of the challenge. The critical thinking, decision-making, and overall architectural direction for the refactoring were guided by the AI's analysis and recommendations.
