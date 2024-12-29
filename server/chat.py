import os

def broadcast_message(udp_socket, client_ports, message):
    """Broadcast a message to all registered UDP client ports."""
    try:
        print(f"Broadcasting to ports: {client_ports}")  # Debugging
        for client_address in client_ports:
            udp_socket.sendto(message.encode(), client_address)
        append_to_chatlog(message)
        print(f"Broadcasted message: {message}")
    except Exception as e:
        print(f"Error broadcasting message: {e}")


def append_to_chatlog(message):
    """Append a message to the chatlog."""
    chatlog_path = os.path.join("data", "chatlog.txt")
    os.makedirs(os.path.dirname(chatlog_path), exist_ok=True)
    with open(chatlog_path, "a") as file:
        file.write(message + "\n")
