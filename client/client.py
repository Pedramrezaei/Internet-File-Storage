import socket
import threading

from utils import validate_username, validate_filename, validate_message

HOST = "145.94.129.189"
PORT = 3000

def receive_messages(client_socket):
    """Thread to handle incoming messages."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print("\n" + message)  # Print the message in real-time
            else:
                break
        except ConnectionResetError:
            print("Disconnected from server.")
            break


def handle_chat(client_socket):
    """Chatroom functionality."""
    print("Welcome to the chatroom! Type your message below.")
    print("Type '!exit' to leave the chatroom.")

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        message = input("> ")
        if message == "!exit":
            client_socket.send("CHAT_EXIT".encode())
            break
        client_socket.send(message.encode())

def list_files(client_socket):
    """List available files on the server."""
    client_socket.send("LIST_FILES".encode())
    files = client_socket.recv(1024).decode()
    print("Available files on server:")
    print(files)

def upload_file(client_socket):
    """Upload a file to the server."""
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

def download_file(client_socket):
    """Download a file from the server."""
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

def preview_file(client_socket):
    """Preview the first few lines of a file."""
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
    """Main client menu."""
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
            list_files(client_socket)
        elif choice == "3":
            upload_file(client_socket)
        elif choice == "4":
            download_file(client_socket)
        elif choice == "5":
            preview_file(client_socket)
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")

def main():
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
            if len(username) < 5:
                print("Username must be at least 5 characters long.")
                continue
            if len(password) < 8:
                print("Password must be at least 8 characters long.")
                continue

            client_socket.send("REGISTER".encode())
            client_socket.send(f"{username}:{password}".encode())
            response = client_socket.recv(1024).decode()
            print(response)
            if response == "Registration successful.":
                print("Please log in to continue.")

        elif option == "2":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            client_socket.send("LOGIN".encode())
            client_socket.send(f"{username}:{password}".encode())
            response = client_socket.recv(1024).decode()
            if response == "LOGIN_SUCCESS":
                print("Login successful.")
                client_menu(client_socket)  # Proceed to main menu
            else:
                print(response)

        elif option == "3":
            print("Exiting the program...")
            client_socket.close()
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
