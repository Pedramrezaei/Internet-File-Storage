def validate_username(username):
    """
    Validate the username:
    - Must be between 5 and 20 characters.
    - Can contain alphanumeric characters and underscores.
    """
    if len(username) < 5 or len(username) > 20:
        return False
    if not username.replace("_", "").isalnum():  # Allow underscores
        return False
    return True


def validate_password(password):
    """
    Validate the password:
    - Must be at least 8 characters long.
    """
    return len(password) >= 8


def validate_filename(filename):
    """
    Validate the filename:
    - Must only contain alphanumeric characters, dots, underscores, and hyphens.
    - Must not contain spaces.
    """
    allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if any(char not in allowed_characters for char in filename):
        return False
    if " " in filename:
        return False
    return True


def validate_message(message):
    """
    Validate the chat message:
    - Length must be between 1 and 500 characters.
    """
    return 1 <= len(message) <= 500
