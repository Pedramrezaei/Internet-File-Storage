from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import pyqtSignal, QSocketNotifier
from .constants import HOST, UDP_PORT

class ChatScreen(QWidget):
    switch_to_main_menu = pyqtSignal()

    def __init__(self, udp_socket, username):
        super().__init__()
        self.udp_socket = udp_socket
        self.username = username
        self.udp_socket.setblocking(False)
        self.udp_socket.bind(("", 0))

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("Welcome to the chat!")

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.back_button = QPushButton("Back to Menu")
        self.back_button.clicked.connect(self.leave_chat)

        self.udp_notifier = QSocketNotifier(self.udp_socket.fileno(), QSocketNotifier.Type.Read)
        self.udp_notifier.activated.connect(self.receive_message)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.send_username_to_server()

    def send_username_to_server(self):
        if self.username:
            try:
                self.udp_socket.sendto(f"SET_USERNAME:{self.username}".encode(), (HOST, UDP_PORT))
            except Exception as e:
                print(f"Error sending username to server: {e}")

    def send_message(self):
        message = self.message_input.text()
        if not message.strip():
            return
        try:
            self.udp_socket.sendto(f"MESSAGE:{message}".encode(), (HOST, UDP_PORT))
            self.message_input.clear()
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_message(self):
        try:
            message, _ = self.udp_socket.recvfrom(1024)
            self.chat_display.append(message.decode())
        except BlockingIOError:
            pass
        except Exception as e:
            print(f"Error receiving message: {e}")

    def leave_chat(self):
        try:
            self.udp_socket.sendto("CHAT_EXIT".encode(), (HOST, UDP_PORT))
        except Exception as e:
            print(f"Error during chat exit: {e}")
        self.switch_to_main_menu.emit()
