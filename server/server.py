import socket
import threading
from auth import register_user, authenticate_user
from file_manager import list_files, save_file, read_file, preview_file
from chat import handle_chat, connected_clients

HOST = "145.94.129.189"
PORT = 3000

clients = []

def handle_client(client_socket):
    """Handle client communication."""
    try:
        while True:
            request = client_socket.recv(1024).decode()
            if request.startswith("LOGIN"):
                username, password = client_socket.recv(1024).decode().split(":")
                success, message = authenticate_user(username, password)
                print(f"Login attempt for {username}: {message}")
                if success:
                    client_socket.send(message.encode())  # Send LOGIN_SUCCESS
                else:
                    client_socket.send(message.encode())  # Send error message
            # Handle other requests...
    except ConnectionResetError:
        print("Client disconnected.")
    finally:
        client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Client connected: {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    main()
