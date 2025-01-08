import os

def broadcast_message(udp_socket, client_ports, message):
    try:
        for ip, port in client_ports.items():
            udp_socket.sendto(message.encode(), (ip, port))
        append_to_chatlog(message)
    except Exception as e:
        print(f"Error broadcasting message: {e}")

def append_to_chatlog(message):
    chatlog_path = os.path.join("data", "chatlog.txt")
    os.makedirs(os.path.dirname(chatlog_path), exist_ok=True)
    with open(chatlog_path, "a") as file:
        file.write(message + "\n")
