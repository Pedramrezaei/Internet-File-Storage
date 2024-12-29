import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHUNK_SIZE = 1024 * 1024  # 1 MB per chunk

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def handle_file_request(request, client_socket):
    """
    Handle file-related requests such as upload, download, list, and preview.
    Args:
        request (str): The request type and details (e.g., "UPLOAD_FILE:filename").
        client_socket (socket.socket): The client socket for communication.
    """
    try:
        if request.startswith("UPLOAD_FILE"):
            filename = request.split(":")[1]
            client_socket.send("READY".encode())  # Acknowledge upload start
            if validate_filename(filename):
                save_file_in_chunks(filename, client_socket)
                client_socket.send(f"{filename} uploaded successfully.".encode())
            else:
                client_socket.send("Invalid filename.".encode())

        elif request.startswith("DOWNLOAD_FILE"):
            filename = request.split(":")[1]
            if validate_filename(filename):
                if not send_file_in_chunks(filename, client_socket):
                    client_socket.send("File not found.".encode())
            else:
                client_socket.send("Invalid filename.".encode())

        elif request == "LIST_FILES":
            files = list_files()
            client_socket.send("\n".join(files).encode())

        elif request.startswith("PREVIEW_FILE"):
            filename = request.split(":")[1]
            if validate_filename(filename):
                preview = preview_file(filename)
                client_socket.send(preview.encode())
            else:
                client_socket.send("Invalid filename.".encode())

        else:
            client_socket.send("Unknown file operation.".encode())
    except Exception as e:
        print(f"Error handling file request: {e}")
        client_socket.send(f"Error: {e}".encode())


def list_files():
    """List all files in the data directory."""
    try:
        return os.listdir(DATA_DIR)
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def save_file_in_chunks(filename, client_socket):
    """Save a file in chunks from the client socket."""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "wb") as file:
            while True:
                chunk = client_socket.recv(CHUNK_SIZE)
                if chunk == b"END":
                    break
                file.write(chunk)
    except Exception as e:
        print(f"Error saving file '{filename}': {e}")


def send_file_in_chunks(filename, client_socket):
    """Send a file in chunks to the client socket."""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"File '{filename}' does not exist.")
            return False
        client_socket.send("READY".encode())  # Acknowledge download start
        with open(filepath, "rb") as file:
            while chunk := file.read(CHUNK_SIZE):
                client_socket.send(chunk)
        client_socket.send(b"END")
        return True
    except Exception as e:
        print(f"Error sending file '{filename}': {e}")
        return False


def preview_file(filename, lines=5):
    """
    Preview the first few lines of a text file.
    Args:
        filename (str): The name of the file to preview.
        lines (int): The number of lines to preview.
    Returns:
        str: The preview of the file as a string, or an error message.
    """
    try:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            return f"File '{filename}' does not exist."
        with open(filepath, "r") as file:
            return "".join(file.readlines()[:lines])
    except Exception as e:
        return f"Error previewing file '{filename}': {e}"


def validate_filename(filename):
    """
    Validate the filename.
    Args:
        filename (str): The name of the file to validate.
    Returns:
        bool: True if the filename is valid, False otherwise.
    """
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    return all(char in allowed_chars for char in filename) and " " not in filename
