import threading
import os

connected_clients = []  # List of all connected client sockets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHATLOG_PATH = os.path.join(BASE_DIR, "data", "chatlog.txt")

# Ensure the data directory and chatlog file exist
if not os.path.exists(os.path.dirname(CHATLOG_PATH)):
    os.makedirs(os.path.dirname(CHATLOG_PATH))
if not os.path.exists(CHATLOG_PATH):
    open(CHATLOG_PATH, "w").close()

def broadcast_message(message, sender_socket=None):
    """Broadcast a message to all connected clients and log it to the chatlog."""
    for client_socket in connected_clients:
        if client_socket != sender_socket:  # Skip the sender
            try:
                client_socket.send(message.encode())
            except:
                client_socket.close()
                connected_clients.remove(client_socket)
    append_to_chatlog(message)

def append_to_chatlog(message):
    """Append a message to the chatlog file."""
    with open(CHATLOG_PATH, "a") as file:
        file.write(message + "\n")

def handle_chat(client_socket, username):
    """Handle chat functionality for a single client."""
    welcome_message = f"Welcome {username} to the chatroom!"
    client_socket.send(welcome_message.encode())
    broadcast_message(f"{username} has joined the chatroom.")

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == "CHAT_EXIT":
                broadcast_message(f"{username} has left the chatroom.")
                break
            broadcast_message(f"{username}: {message}", sender_socket=client_socket)
        except:
            broadcast_message(f"{username} has disconnected.")
            break
    if client_socket in connected_clients:
        connected_clients.remove(client_socket)
