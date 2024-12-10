import threading

chat_history = []

def add_message(username, message):
    """Add a message to the chat history."""
    global chat_history
    chat_history.append(f"{username}: {message}")
    if len(chat_history) > 100:  # Limit chat history to 100 messages
        chat_history.pop(0)

def get_chat_history():
    """Get the full chat history."""
    return "\n".join(chat_history)

def handle_chat(client_socket, username):
    """Handle chat functionality for a client."""
    client_socket.send("Welcome to the chatroom!".encode())
    client_socket.send(get_chat_history().encode())
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == "CHAT_EXIT":
                break
            add_message(username, message)
            print(f"{username}: {message}")
        except ConnectionResetError:
            print(f"User {username} disconnected from chat.")
            break
