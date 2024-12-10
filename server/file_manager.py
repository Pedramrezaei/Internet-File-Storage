import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def list_files():
    """List all files in the data directory."""
    return os.listdir(DATA_DIR)

def save_file(filename, data):
    """Save a file to the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "wb") as file:
        file.write(data)

def read_file(filename):
    """Read a file from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as file:
        return file.read()

def preview_file(filename, lines=5):
    """Preview the first few lines of a file."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as file:
        return "".join(file.readlines()[:lines])
