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
            if request.startswith("CHAT"):
                username = request.split(":")[1]
                if client_socket not in connected_clients:
                    connected_clients.append(client_socket)
                handle_chat(client_socket, username)
    except ConnectionResetError:
        print("Client disconnected.")
    finally:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
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
