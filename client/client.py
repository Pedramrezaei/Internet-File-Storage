import socket
import threading
from utils import validate_username, validate_password, validate_filename, validate_message

HOST = "145.94.177.193" # Same IP as server ip (Pedram laptop)
PORT = 1701


def receive_messages(client_socket):
    """Thread to handle incoming messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print("\n" + message)  # Display messages in real-time
            else:
                break
        except ConnectionResetError:
            print("Disconnected from server.")
            break


def handle_chat(client_socket):
    """Chatroom functionality."""
    print("Welcome to the chatroom! Type your messages below.")
    print("Type '!exit' to leave the chatroom.")

    # Start a thread to listen for incoming messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        message = input("> ")
        if message.strip().lower() == "!exit":
            client_socket.send("CHAT_EXIT".encode())
            break
        if validate_message(message):
            client_socket.send(message.encode())
        else:
            print("Invalid message. Ensure it is between 1 and 500 characters.")


def handle_file_operations(client_socket, operation):
    """Handle file-related operations: list, upload, download, or preview."""
    if operation == "LIST_FILES":
        client_socket.send("LIST_FILES".encode())
        files = client_socket.recv(1024).decode()
        print("Available files on server:")
        print(files)

    elif operation == "UPLOAD_FILE":
        file_name = input("Enter the file name to upload: ")
        if not validate_filename(file_name):
            print("Invalid filename.")
            return

        try:
            with open(file_name, "rb") as file:
                file_data = file.read()
            client_socket.send(f"UPLOAD_FILE:{file_name}".encode())
            client_socket.send(file_data)
            response = client_socket.recv(1024).decode()
            print(response)
        except FileNotFoundError:
            print("File not found.")

    elif operation == "DOWNLOAD_FILE":
        file_name = input("Enter the file name to download: ")
        if not validate_filename(file_name):
            print("Invalid filename.")
            return

        client_socket.send(f"DOWNLOAD_FILE:{file_name}".encode())
        response = client_socket.recv(1024).decode()
        if response == "File downloaded successfully.":
            with open(file_name, "wb") as file:
                file_data = client_socket.recv(1024 * 1024)
                file.write(file_data)
            print(f"{file_name} downloaded successfully.")
        else:
            print(response)

    elif operation == "PREVIEW_FILE":
        file_name = input("Enter the file name to preview: ")
        if not validate_filename(file_name):
            print("Invalid filename.")
            return

        client_socket.send(f"PREVIEW_FILE:{file_name}".encode())
        response = client_socket.recv(1024).decode()
        if response.startswith("File preview:"):
            print(response[len("File preview:"):])
        else:
            print(response)


def client_menu(client_socket):
    """Main menu after login."""
    while True:
        print("\nMenu:")
        print("1. Join Chatroom")
        print("2. List Files")
        print("3. Upload File")
        print("4. Download File")
        print("5. Preview File")
        print("6. Logout")
        choice = input("Select an option: ")

        if choice == "1":
            handle_chat(client_socket)
        elif choice == "2":
            handle_file_operations(client_socket, "LIST_FILES")
        elif choice == "3":
            handle_file_operations(client_socket, "UPLOAD_FILE")
        elif choice == "4":
            handle_file_operations(client_socket, "DOWNLOAD_FILE")
        elif choice == "5":
            handle_file_operations(client_socket, "PREVIEW_FILE")
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")


def main():
    """Client main entry point."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    while True:
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        option = input("Select an option: ")

        if option == "1":
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            if not validate_username(username):
                print("Username must be at least 5 characters and alphanumeric.")
                continue
            if not validate_password(password):
                print("Password must be at least 8 characters.")
                continue

            client_socket.send("REGISTER".encode())
            client_socket.send(f"{username}:{password}".encode())
            response = client_socket.recv(1024).decode()
            print(response)

        elif option == "2":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            client_socket.send("LOGIN".encode())
            client_socket.send(f"{username}:{password}".encode())
            response = client_socket.recv(1024).decode()
            print(f"Server response: {response}")
            if response == "LOGIN_SUCCESS":
                print("Login successful. Redirecting to the menu...")
                client_menu(client_socket)
            else:
                print(response)

        elif option == "3":
            client_socket.close()
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
