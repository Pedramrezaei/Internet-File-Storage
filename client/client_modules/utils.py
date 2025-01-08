def validate_username(username):
    return 5 <= len(username) <= 20 and username.replace("_", "").isalnum()

def validate_password(password):
    return len(password) >= 8

def validate_filename(filename):
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    return all(char in allowed_chars for char in filename) and " " not in filename

def validate_message(message):
    return 1 <= len(message) <= 500
