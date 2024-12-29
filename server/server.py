import socket
import threading
from chat import broadcast_message
from auth import authenticate_user, register_user
from utils import validate_username, validate_password
import time

TCP_HOST = "145.94.130.217"
TCP_PORT = 1500
UDP_PORT = 1701

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udp_socket.bind((TCP_HOST, UDP_PORT))

client_ports = {}  # Track clients with IP as key and port as value
usernames = {}  # Track usernames with IP as key
processed_messages = set()  # Use a combination of message and timestamp


def handle_client(client_socket, client_address):
    global client_ports, usernames
    print(f"New connection from {client_address}")
    ip, port = client_address
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
                    print(f"{username} logged in successfully.")
                    usernames[ip] = username  # Save username for this IP
                    client_socket.send("LOGIN_SUCCESS".encode())
            elif request == "CHAT_EXIT":
                if ip in usernames:
                    del usernames[ip]
                break
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()
        if ip in client_ports:
            del client_ports[ip]
            print(f"Removed {client_address} from client_ports.")
        print(f"Connection with {client_address} closed.")


def handle_udp_messages():
    global client_ports, usernames
    print("Listening for UDP messages...")
    while True:
        try:
            message, client_address = udp_socket.recvfrom(1024)
            message = message.decode()
            ip, port = client_address

            # Register or update client port
            client_ports[ip] = port

            # Handle SET_USERNAME command
            if message.startswith("SET_USERNAME:"):
                username = message.split(":", 1)[1]
                usernames[ip] = username
                print(f"Username set for {ip}: {username}")
                continue

            # Handle client exit
            if message == "CHAT_EXIT":
                if ip in client_ports:
                    del client_ports[ip]
                if ip in usernames:
                    del usernames[ip]
                print(f"Removed {client_address} from client_ports and usernames.")
                continue

            # Append username if it exists
            if message.startswith("MESSAGE:"):
                if ip in usernames:
                    username = usernames[ip]
                    content = message.split(":", 1)[1]  # Extract message content
                    message = f"{username}: {content}"
                else:
                    message = f"Unknown: {message.split(':', 1)[1]}"

            # Broadcast the message
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
