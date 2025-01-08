import os
from datetime import datetime

FILES_DIR = os.path.join("data", "files")
METADATA_PATH = os.path.join("data", "metadata.txt")

# Ensure the necessary directories exist
os.makedirs(FILES_DIR, exist_ok=True)
if not os.path.exists(METADATA_PATH):
    open(METADATA_PATH, "w").close()


def list_files():
    """List all files and their metadata."""
    files = []
    with open(METADATA_PATH, "r") as metadata_file:
        for line in metadata_file:
            name, description, date_uploaded, file_type, size = line.strip().split("|")
            files.append({
                "name": name,
                "description": description,
                "date_uploaded": date_uploaded,
                "type": file_type,
                "size": size,
            })
    return files


def upload_file(filename, description, file_data):
    """Upload a file and store its metadata."""
    filepath = os.path.join(FILES_DIR, filename)
    with open(filepath, "wb") as file:
        file.write(file_data)

    size = os.path.getsize(filepath)
    file_type = filename.split(".")[-1]
    date_uploaded = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append metadata to the file
    with open(METADATA_PATH, "a") as metadata_file:
        metadata_file.write(f"{filename}|{description}|{date_uploaded}|{file_type}|{size}\n")


def download_file(filename):
    """Download a file from the server."""
    filepath = os.path.join(FILES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as file:
            return file.read()
    return None


def preview_file(filename, lines=5):
    """Preview the first few lines of a text file."""
    filepath = os.path.join(FILES_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as file:
                return "".join(file.readlines()[:lines])
        except Exception as e:
            return f"Error previewing file: {e}"
    return f"File '{filename}' does not exist."
