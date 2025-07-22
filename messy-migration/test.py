import requests
import json
import random
import string
import time # For unique email generation

BASE_URL = "http://localhost:5000"

def generate_unique_email():
    """Generates a unique email address for testing purposes."""
    timestamp = int(time.time() * 1000)
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"test_user_{timestamp}_{random_string}@example.com"

def test_health_check():
    """Tests the GET / endpoint."""
    print("\n--- Testing GET / (Health Check) ---")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json().get("message") == "User Management System API is running!"
    print("Health check PASSED.")

def test_get_all_users():
    """Tests the GET /users endpoint."""
    print("\n--- Testing GET /users ---")
    response = requests.get(f"{BASE_URL}/users")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert "users" in response.json()
    assert isinstance(response.json()["users"], list)
    print("Get all users PASSED.")
    return response.json()["users"]

def test_create_user_success():
    """Tests POST /users for successful user creation."""
    print("\n--- Testing POST /users (Success) ---")
    unique_email = generate_unique_email()
    user_data = {
        "name": "New Test User",
        "email": unique_email,
        "password": "securePassword123"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json().get("message") == "User created successfully!"
    print("Create user (success) PASSED.")
    return response.json().get("id"), unique_email

def test_create_user_duplicate_email():
    """Tests POST /users for duplicate email conflict."""
    print("\n--- Testing POST /users (Duplicate Email Conflict) ---")
    # Use an email that is known to exist from init_db.py or a previous test
    duplicate_email = "john@example.com" 
    user_data = {
        "name": "Duplicate User",
        "email": duplicate_email,
        "password": "anypassword"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
    # --- DEBUGGING PRINTS ---
    print(f"DEBUG: Actual status code type: {type(response.status_code)}, value: {response.status_code}")
    print(f"DEBUG: Expected status code type: {type(409)}, value: {409}")
    # --- END DEBUGGING PRINTS ---

    assert response.status_code == 409
    assert response.json().get("error") == "Conflict"
    assert response.json().get("message") == "User with this email already exists."
    print("Create user (duplicate email) PASSED.")

def test_create_user_missing_data():
    """Tests POST /users for missing required fields."""
    print("\n--- Testing POST /users (Missing Data) ---")
    user_data = {
        "name": "Incomplete User",
        "email": "incomplete@example.com" # Password is missing
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 400
    assert response.json().get("error") == "Missing Data"
    print("Create user (missing data) PASSED.")

def test_create_user_invalid_email():
    """Tests POST /users for invalid email format."""
    print("\n--- Testing POST /users (Invalid Email) ---")
    user_data = {
        "name": "Invalid Email User",
        "email": "invalid-email", # Missing @ and domain
        "password": "password"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 400
    assert response.json().get("error") == "Invalid Email"
    print("Create user (invalid email) PASSED.")

def test_create_user_weak_password():
    """Tests POST /users for weak password."""
    print("\n--- Testing POST /users (Weak Password) ---")
    user_data = {
        "name": "Weak Pass User",
        "email": generate_unique_email(),
        "password": "short" # Less than 8 characters
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
    # --- DEBUGGING PRINTS ---
    print(f"DEBUG: Actual status code type: {type(response.status_code)}, value: {response.status_code}")
    print(f"DEBUG: Expected status code type: {type(400)}, value: {400}")
    # --- END DEBUGGING PRINTS ---

    assert response.status_code == 400
    assert response.json().get("error") == "Weak Password"
    print("Create user (weak password) PASSED.")

def test_get_specific_user(user_id):
    """Tests GET /user/<id>."""
    print(f"\n--- Testing GET /user/{user_id} ---")
    response = requests.get(f"{BASE_URL}/user/{user_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json().get("user", {}).get("id") == user_id
    print(f"Get specific user {user_id} PASSED.")

def test_get_non_existent_user():
    """Tests GET /user/<id> for a non-existent user."""
    print("\n--- Testing GET /user/9999 (Non-existent) ---")
    response = requests.get(f"{BASE_URL}/user/9999")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 404
    assert response.json().get("message") == "User not found"
    print("Get non-existent user PASSED.")

def test_update_user_success(user_id):
    """Tests PUT /user/<id> for successful update."""
    print(f"\n--- Testing PUT /user/{user_id} (Success) ---")
    update_data = {
        "name": "Updated Name",
        "email": generate_unique_email() # Update with a new unique email
    }
    response = requests.put(f"{BASE_URL}/user/{user_id}", json=update_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json().get("message") == "User updated successfully!"
    print(f"Update user {user_id} (success) PASSED.")

def test_update_user_no_data(user_id):
    """Tests PUT /user/<id> with no update data."""
    print(f"\n--- Testing PUT /user/{user_id} (No Data) ---")
    headers = {"Content-Type": "application/json"} # Explicitly set header
    response = requests.put(f"{BASE_URL}/user/{user_id}", headers=headers, data=json.dumps({})) # Send empty JSON string
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}") # Print raw text to avoid json.dumps error if not JSON
    
    try:
        response_json = response.json()
        print(f"Parsed Response Body: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        response_json = {} # Or handle as appropriate if not JSON
        print("Response body is not valid JSON.")

    # --- DEBUGGING PRINTS ---
    print(f"DEBUG: Actual status code type: {type(response.status_code)}, value: {response.status_code}")
    print(f"DEBUG: Expected status code type: {type(400)}, value: {400}")
    # --- END DEBUGGING PRINTS ---

    assert response.status_code == 400
    assert response_json.get("error") == "No Data" # Assert against parsed JSON
    print(f"Update user {user_id} (no data) PASSED.")

def test_update_user_non_existent(user_id=9999):
    """Tests PUT /user/<id> for a non-existent user."""
    print(f"\n--- Testing PUT /user/{user_id} (Non-existent) ---")
    update_data = {"name": "Non Existent Update"}
    response = requests.put(f"{BASE_URL}/user/{user_id}", json=update_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 404
    assert response.json().get("message") == "User not found"
    print(f"Update user {user_id} (non-existent) PASSED.")

def test_search_users(search_term):
    """Tests GET /search?name=<name>."""
    print(f"\n--- Testing GET /search?name={search_term} ---")
    response = requests.get(f"{BASE_URL}/search?name={search_term}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert "users" in response.json()
    assert isinstance(response.json()["users"], list)
    print(f"Search users for '{search_term}' PASSED.")

def test_search_users_missing_param():
    """Tests GET /search with missing name parameter."""
    print("\n--- Testing GET /search (Missing Parameter) ---")
    response = requests.get(f"{BASE_URL}/search")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 400
    assert response.json().get("error") == "Missing Parameter"
    print("Search users (missing parameter) PASSED.")

def test_login_success(email, password):
    """Tests POST /login for successful login."""
    print(f"\n--- Testing POST /login (Success for {email}) ---")
    login_data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json().get("status") == "success"
    assert response.json().get("message") == "Login successful!"
    print("Login (success) PASSED.")

def test_login_failed(email, password):
    """Tests POST /login for failed login (invalid credentials)."""
    print(f"\n--- Testing POST /login (Failed for {email}) ---")
    login_data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 401
    assert response.json().get("status") == "failed"
    assert response.json().get("message") == "Invalid email or password."
    print("Login (failed) PASSED.")

def test_delete_user_success(user_id):
    """Tests DELETE /user/<id> for successful deletion."""
    print(f"\n--- Testing DELETE /user/{user_id} (Success) ---")
    response = requests.delete(f"{BASE_URL}/user/{user_id}")
    print(f"Status Code: {response.status_code}")
    # 204 No Content should have an empty body, so response.json() will fail
    print(f"Response Body: '{response.text}' (Expected empty for 204)")
    assert response.status_code == 204
    print(f"Delete user {user_id} (success) PASSED.")

def test_delete_user_non_existent(user_id=9999):
    """Tests DELETE /user/<id> for a non-existent user."""
    print(f"\n--- Testing DELETE /user/{user_id} (Non-existent) ---")
    response = requests.delete(f"{BASE_URL}/user/{user_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 404
    assert response.json().get("message") == "User not found"
    print(f"Delete user {user_id} (non-existent) PASSED.")


if __name__ == "__main__":
    print("--- Starting API Endpoint Tests ---")
    print("Ensure the Flask application is running on http://localhost:5000")
    print("Also ensure 'python init_db.py' has been run recently for a clean database state.")
    print("IMPORTANT: Ensure your app.py is the latest version with all refactoring changes.\n")

    # Run all tests
    test_health_check()
    
    # Test user creation scenarios
    new_user_id_1, new_user_email_1 = test_create_user_success()
    test_create_user_duplicate_email() # This should correctly return 409
    test_create_user_missing_data()
    test_create_user_invalid_email()
    test_create_user_weak_password()

    # Test GET operations
    test_get_all_users()
    if new_user_id_1:
        test_get_specific_user(new_user_id_1)
    test_get_specific_user(1) # Test with an ID from init_db.py
    test_get_non_existent_user()

    # Test update operations
    if new_user_id_1:
        test_update_user_success(new_user_id_1)
        # Verify the update by fetching the user again (optional but good practice)
        test_get_specific_user(new_user_id_1) 
        test_update_user_no_data(new_user_id_1)
    test_update_user_non_existent()

    # Test search operations
    test_search_users("john")
    test_search_users("test") # Should find "New Test User" if created
    test_search_users("nonexistent") # Should return empty list
    test_search_users_missing_param()

    # Test login operations
    test_login_success("john@example.com", "password123")
    test_login_failed("john@example.com", "wrongpass")
    test_login_failed("nonexistent@example.com", "anypass")

    # Test delete operations (perform deletion last on a created user)
    if new_user_id_1:
        test_delete_user_success(new_user_id_1)
        # Verify deletion
        test_get_non_existent_user() # Should now be 404 for the deleted ID
    test_delete_user_non_existent()

    print("\n--- All API Endpoint Tests Completed ---")
