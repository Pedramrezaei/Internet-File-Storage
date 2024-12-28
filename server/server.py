import socket
import threading
from chat import handle_chat, connected_clients
from auth import authenticate_user, register_user
from utils import validate_username, validate_password

HOST = "145.94.177.193"
PORT = 1700

def handle_client(client_socket):
    """Handle client communication."""
    try:
        while True:
            request = client_socket.recv(1024).decode()
            if request == "REGISTER":
                credentials = client_socket.recv(1024).decode().split(":")
                username, password = credentials[0], credentials[1]
                if not validate_username(username) or not validate_password(password):
                    client_socket.send("Invalid credentials.".encode())
                else:
                    success, message = register_user(username, password)
                    client_socket.send(message.encode())

            elif request == "LOGIN":
                credentials = client_socket.recv(1024).decode().split(":")
                username, password = credentials[0], credentials[1]
                success, message = authenticate_user(username, password)
                client_socket.send(message.encode())
                if success:
                    if client_socket not in connected_clients:
                        connected_clients.append(client_socket)
                    handle_chat(client_socket, username)

    except Exception as e:
        print(f"Error in handle_client: {e}")
    finally:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
        client_socket.close()

def start_server():
    """Start the server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Client connected: {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
