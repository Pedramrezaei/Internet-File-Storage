import os

def broadcast_message(udp_socket, client_ports, message):
    """Broadcast a message to all registered UDP client ports."""
    try:
        print(f"Broadcasting to clients: {client_ports}")  # Debugging
        for ip, port in client_ports.items():  # Iterate over IP and port
            udp_socket.sendto(message.encode(), (ip, port))
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
