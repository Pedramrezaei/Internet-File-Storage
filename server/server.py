import socket
import threading
from auth import register_user, authenticate_user
from file_manager import list_files, save_file, read_file, preview_file
from chat import handle_chat

HOST = "145.94.129.189"
PORT = 3000

clients = []

def handle_client(client_socket):
    """Handle client communication."""
    try:
        while True:
            request = client_socket.recv(1024).decode()
            if request.startswith("REGISTER"):
                username, password = client_socket.recv(1024).decode().split(":")
                success, message = register_user(username, password)
                client_socket.send(message.encode())
            elif request.startswith("LOGIN"):
                username, password = client_socket.recv(1024).decode().split(":")
                success, message = authenticate_user(username, password)
                if success:
                    client_socket.send("LOGIN_SUCCESS".encode())
                else:
                    client_socket.send(message.encode())
            elif request.startswith("LIST_FILES"):
                files = "\n".join(list_files())
                client_socket.send(files.encode())
            elif request.startswith("UPLOAD_FILE"):
                filename = request.split(":")[1]
                data = client_socket.recv(1024 * 1024)
                save_file(filename, data)
                client_socket.send("File uploaded successfully.".encode())
            elif request.startswith("DOWNLOAD_FILE"):
                filename = request.split(":")[1]
                data = read_file(filename)
                if data:
                    client_socket.send("File downloaded successfully.".encode())
                    client_socket.send(data)
                else:
                    client_socket.send("File not found.".encode())
            elif request.startswith("PREVIEW_FILE"):
                filename = request.split(":")[1]
                preview = preview_file(filename)
                if preview:
                    client_socket.send(f"File preview:\n{preview}".encode())
                else:
                    client_socket.send("File not found.".encode())
            elif request.startswith("CHAT"):
                username, message = request.split(":")
                handle_chat(client_socket, username)
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
