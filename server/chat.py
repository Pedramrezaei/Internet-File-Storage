import os

connected_clients = []  # List to store all connected client sockets

def broadcast_message(message, sender_socket=None):
    """Broadcast a message to all connected clients except the sender and log it."""
    print(f"Broadcasting message: {message}")  # Debugging log
    for client_socket in connected_clients:
        if client_socket != sender_socket:  # Avoid sending the message back to the sender
            try:
                client_socket.send(message.encode())
            except Exception as e:
                print(f"Error sending message to a client: {e}")
                client_socket.close()
                connected_clients.remove(client_socket)
    append_to_chatlog(message)

def append_to_chatlog(message):
    """Append a message to the chatlog.txt file."""
    chatlog_path = os.path.join("data", "chatlog.txt")
    with open(chatlog_path, "a") as file:
        file.write(message + "\n")

def handle_chat(client_socket, username):
    """Handle chat functionality for a single client."""
    welcome_message = f"{username} has joined the chatroom."
    broadcast_message(welcome_message)
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message.strip().lower() == "!exit":
                broadcast_message(f"{username} has left the chatroom.")
                break
            broadcast_message(f"{username}: {message}", sender_socket=client_socket)
    except Exception as e:
        print(f"Error in chat handling for {username}: {e}")
    finally:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
        client_socket.close()
