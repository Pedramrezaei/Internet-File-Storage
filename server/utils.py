# Input Validation
def validate_username(username):
    if len(username) < 5 or len(username) > 20:
        return False
    if not username.isalnum() and "_" not in username:
        return False
    return True

def validate_filename(filename):
    allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if any(char not in allowed_characters for char in filename):
        return False
    if " " in filename:
        return False
    return True

def validate_message(message):
    if len(message) == 0 or len(message) > 500:
        return False
    return True
