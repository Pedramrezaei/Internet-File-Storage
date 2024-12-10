import os

def validate_username(username):
    """Validates a username to ensure it is alphanumeric and 5-20 characters long."""
    return username.isalnum() and 5 <= len(username) <= 20

def validate_password(password):
    """Validates a password to ensure it is at least 8 characters long."""
    return len(password) >= 8

def validate_message(message):
    """Validates a message to ensure it is between 1 and 500 characters."""
    return 1 <= len(message) <= 500

def validate_filename(filename):
    """Validates a filename to ensure it is alphanumeric or contains valid special characters."""
    allowed_chars = "._-"
    return (
        1 <= len(filename) <= 255
        and all(c.isalnum() or c in allowed_chars for c in filename)
        and not filename.startswith(".")
    )
