import bcrypt
import os

# Set the path for credentials.txt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CREDENTIALS_PATH = os.path.join(DATA_DIR, "credentials.txt")

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_credentials():
    """Load credentials from the credentials file."""
    if not os.path.exists(CREDENTIALS_PATH):
        open(CREDENTIALS_PATH, "w").close()  # Create the file if it doesn't exist
        return {}
    with open(CREDENTIALS_PATH, 'r') as file:
        credentials = {}
        for line in file:
            username, hashed_password = line.strip().split(":")
            credentials[username] = hashed_password
    return credentials

def save_credentials(credentials):
    """Save credentials to the credentials file."""
    with open(CREDENTIALS_PATH, 'w') as file:
        for username, hashed_password in credentials.items():
            file.write(f"{username}:{hashed_password}\n")

def register_user(username, password):
    """Register a new user."""
    credentials = load_credentials()
    if username in credentials:
        return False, "User already exists."
    if len(password) < 8:
        return False, "Password too short."
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    credentials[username] = hashed_password
    save_credentials(credentials)
    return True, "Registration successful."

def authenticate_user(username, password):
    """Authenticate an existing user."""
    credentials = load_credentials()
    if username in credentials:
        if bcrypt.checkpw(password.encode(), credentials[username].encode()):
            return True, "Login successful."
        return False, "Incorrect password."
    return False, "User not found."
