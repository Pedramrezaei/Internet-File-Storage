import socket
import threading
from server_modules.chat import broadcast_message
from server_modules.auth import authenticate_user, register_user
from server_modules.file_manager import list_files, upload_file, download_file, preview_file
from server_modules.utils import validate_username, validate_password

TCP_HOST = "145.94.179.166"
TCP_PORT = 1501
UDP_PORT = 1702

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udp_socket.bind((TCP_HOST, UDP_PORT))

client_ports = {}
usernames = {}


def handle_client(client_socket, client_address):
    global client_ports, usernames
    ip, port = client_address
    try:
        while True:
            request = client_socket.recv(1024).decode(errors="ignore").strip()
            if request == "REGISTER":
                credentials = client_socket.recv(1024).decode().strip().split(":")
                username, password = credentials[0], credentials[1]
                if not validate_username(username) or not validate_password(password):
                    client_socket.send("Invalid credentials.".encode())
                else:
                    success, message = register_user(username, password)
                    client_socket.send(message.encode())
            elif request == "LOGIN":
                credentials = client_socket.recv(1024).decode().strip().split(":")
                username, password = credentials[0], credentials[1]
                success, message = authenticate_user(username, password)
                client_socket.send(message.encode())
                if success:
                    usernames[ip] = username
                    client_socket.send("LOGIN_SUCCESS".encode())
            elif request == "CHAT_EXIT":
                if ip in usernames:
                    del usernames[ip]
                break
            elif request == "LIST_FILES":
                files = list_files()
                formatted_files = "\n".join(files) if files else ""
                try:
                    client_socket.send(formatted_files.encode("utf-8"))
                except Exception as e:
                    print(f"Error sending file list: {e}")
            elif request.startswith("UPLOAD_FILE"):
                try:
                    metadata = request.split(":")[1]
                    filename, description = metadata.split("|")
                    file_data = client_socket.recv(1024 * 1024)
                    upload_file(filename, description, file_data)
                    client_socket.send("File uploaded successfully.".encode())
                except Exception as e:
                    client_socket.send(f"UPLOAD_ERROR: {e}".encode())
            elif request.startswith("DOWNLOAD_FILE"):
                filename = request.split(":")[1]
                file_data = download_file(filename)
                if file_data:
                    client_socket.send(file_data)
                else:
                    client_socket.send(f"File '{filename}' not found.".encode())
            elif request.startswith("PREVIEW_FILE"):
                filename = request.split(":")[1]
                preview = preview_file(filename)
                client_socket.send(preview.encode())
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()
        if ip in client_ports:
            del client_ports[ip]
        print(f"Connection with {client_address} closed.")


def handle_udp_messages():
    global client_ports, usernames
    while True:
        try:
            message, client_address = udp_socket.recvfrom(1024)
            message = message.decode().strip()
            ip, port = client_address

            client_ports[ip] = port

            if message == "CHAT_EXIT":
                if ip in client_ports:
                    del client_ports[ip]
                if ip in usernames:
                    del usernames[ip]
                continue

            if message.startswith("SET_USERNAME:"):
                username = message.split(":", 1)[1]
                usernames[ip] = username
                continue

            if message.startswith("MESSAGE:"):
                if ip in usernames:
                    username = usernames[ip]
                    content = message.split(":", 1)[1]
                    message = f"{username}: {content}"
                else:
                    message = f"Unknown: {message.split(':', 1)[1]}"

            broadcast_message(udp_socket, client_ports, message)
        except Exception as e:
            print(f"Error in UDP message handling: {e}")


def start_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((TCP_HOST, TCP_PORT))
    tcp_socket.listen(5)
    print(f"Server started on {TCP_HOST}:{TCP_PORT} (TCP) and {UDP_PORT} (UDP)")

    threading.Thread(target=handle_udp_messages, daemon=True).start()

    while True:
        client_socket, client_address = tcp_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()


if __name__ == "__main__":
    start_server()
