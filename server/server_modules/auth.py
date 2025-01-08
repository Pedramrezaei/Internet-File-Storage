import bcrypt
import os

credentials_path = os.path.join("data", "credentials.txt")

def load_credentials():
    if not os.path.exists(credentials_path):
        return {}
    with open(credentials_path, "r") as file:
        lines = file.readlines()
    credentials = {}
    for line in lines:
        username, hashed_password = line.strip().split(":")
        credentials[username] = hashed_password
    return credentials

def save_credentials(credentials):
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
    with open(credentials_path, "w") as file:
        for username, hashed_password in credentials.items():
            file.write(f"{username}:{hashed_password}\n")

def authenticate_user(username, password):
    credentials = load_credentials()
    if username in credentials:
        if bcrypt.checkpw(password.encode(), credentials[username].encode()):
            return True, "LOGIN_SUCCESS"
        return False, "Incorrect password."
    return False, "User not found."

def register_user(username, password):
    credentials = load_credentials()
    if username in credentials:
        return False, "User already exists."
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    credentials[username] = hashed_password
    save_credentials(credentials)
    return True, "Registration successful."
