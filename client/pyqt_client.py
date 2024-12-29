from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSocketNotifier
import socket

HOST = "145.94.130.217"
TCP_PORT = 1500
UDP_PORT = 1701


class LoginScreen(QWidget):
    switch_to_main = pyqtSignal()

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password")
        self.layout.addWidget(self.password_input)
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)
        self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText("Username and password cannot be empty.")
            return
        try:
            self.client_socket.sendall("LOGIN".encode())
            self.client_socket.sendall(f"{username}:{password}".encode())
            response = self.client_socket.recv(1024).decode()
            if response == "LOGIN_SUCCESS":
                self.switch_to_main.emit()
            else:
                self.status_label.setText(response)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText("Username and password cannot be empty.")
            return
        try:
            self.client_socket.sendall("REGISTER".encode())
            self.client_socket.sendall(f"{username}:{password}".encode())
            response = self.client_socket.recv(1024).decode()
            self.status_label.setText(response)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")


class MainMenuScreen(QWidget):
    switch_to_chat = pyqtSignal()
    switch_to_file_manager = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        chat_button = QPushButton("Join Chatroom")
        chat_button.clicked.connect(self.switch_to_chat)
        layout.addWidget(chat_button)
        file_manager_button = QPushButton("File Manager")
        file_manager_button.clicked.connect(self.switch_to_file_manager)
        layout.addWidget(file_manager_button)
        self.setLayout(layout)


class ChatScreen(QWidget):
    def __init__(self, udp_socket):
        super().__init__()
        self.udp_socket = udp_socket
        self.udp_socket.setblocking(False)
        self.udp_socket.bind(("", 0))  # Dynamically bind to an available port
        print(f"UDP socket bound to {self.udp_socket.getsockname()}")  # Debugging

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("This is the start of your chatting experience.")
        print("Chat display initialized with starting message.")  # Debugging

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.udp_notifier = QSocketNotifier(self.udp_socket.fileno(), QSocketNotifier.Type.Read)
        self.udp_notifier.activated.connect(self.receive_message)
        print(f"UDP notifier initialized: {self.udp_notifier}")  # Debugging

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        self.setLayout(layout)
        print("ChatScreen layout and widgets set.")  # Debugging

    def send_message(self):
        message = self.message_input.text()
        if not message.strip():
            print("No message to send.")  # Debugging
            return
        try:
            self.udp_socket.sendto(message.encode(), (HOST, UDP_PORT))
            print(f"Message sent: {message}")  # Debugging
            self.message_input.clear()
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_message(self):
        print("receive_message triggered")  # Debugging
        try:
            message, _ = self.udp_socket.recvfrom(1024)
            decoded_message = message.decode()
            print(f"Message received: {decoded_message}")  # Debugging
            self.chat_display.append(decoded_message)
            print(f"Chat display updated with: {decoded_message}")  # Debugging
        except BlockingIOError:
            print("No message received yet.")  # Debugging
        except Exception as e:
            print(f"Error receiving message: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Client")
        self.setGeometry(200, 200, 600, 400)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, TCP_PORT))
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.login_screen = LoginScreen(self.client_socket)
        self.main_menu_screen = MainMenuScreen()
        self.chat_screen = ChatScreen(self.udp_socket)
        self.login_screen.switch_to_main.connect(self.show_main_menu)
        self.main_menu_screen.switch_to_chat.connect(self.show_chat)
        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.main_menu_screen)
        self.stack.addWidget(self.chat_screen)
        self.stack.setCurrentWidget(self.login_screen)

    def show_main_menu(self):
        self.stack.setCurrentWidget(self.main_menu_screen)

    def show_chat(self):
        self.stack.setCurrentWidget(self.chat_screen)

    def closeEvent(self, event):
        try:
            self.client_socket.send("CHAT_EXIT".encode())
            self.client_socket.close()
            self.udp_socket.close()
        except Exception as e:
            print(f"Error during client disconnect: {e}")
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
