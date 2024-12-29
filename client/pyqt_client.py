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

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        chat_button = QPushButton("Join Chatroom")
        chat_button.clicked.connect(self.switch_to_chat)
        layout.addWidget(chat_button)
        self.setLayout(layout)


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
        """Send the username to the server to associate it with the client."""
        if self.username:
            try:
                self.udp_socket.sendto(f"SET_USERNAME:{self.username}".encode(), (HOST, UDP_PORT))
                print(f"Username '{self.username}' sent to the server.")
            except Exception as e:
                print(f"Error sending username to server: {e}")

    def send_message(self):
        message = self.message_input.text()
        if not message.strip():
            return
        try:
            formatted_message = f"MESSAGE:{message}"  # Send only the message content
            self.udp_socket.sendto(formatted_message.encode(), (HOST, UDP_PORT))
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.username = None
        self.setWindowTitle("Chat Client")
        self.setGeometry(200, 200, 600, 400)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, TCP_PORT))
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.login_screen = LoginScreen(self.client_socket)
        self.main_menu_screen = MainMenuScreen()
        self.chat_screen = None  # Initialize chat_screen later
        self.login_screen.switch_to_main.connect(self.show_main_menu)
        self.main_menu_screen.switch_to_chat.connect(self.show_chat)

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.main_menu_screen)
        self.stack.setCurrentWidget(self.login_screen)

    def show_main_menu(self):
        self.username = self.login_screen.username_input.text()
        self.stack.setCurrentWidget(self.main_menu_screen)

    def show_chat(self):
        if self.chat_screen is None:  # Create the chat screen only once
            self.chat_screen = ChatScreen(self.udp_socket, self.username)
            self.chat_screen.switch_to_main_menu.connect(self.show_main_menu)
            self.stack.addWidget(self.chat_screen)

        self.chat_screen.username = self.username
        self.chat_screen.send_username_to_server()  # Ensure username is sent
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
