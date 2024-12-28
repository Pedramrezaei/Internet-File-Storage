from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QWidget, QLabel, QFormLayout
import socket
import threading


class LoginScreen(QWidget):
    def __init__(self, switch_to_main, client_socket):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.client_socket = client_socket

        # Layout
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        layout.addRow("Password:", self.password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username and password:
            # Send login details to the server
            self.client_socket.send(f"LOGIN:{username}:{password}".encode())
            response = self.client_socket.recv(1024).decode()
            if response == "LOGIN_SUCCESS":
                self.switch_to_main(username)
            else:
                self.username_input.setText("")
                self.password_input.setText("")
                self.username_input.setPlaceholderText("Invalid login. Try again.")


class ChatScreen(QWidget):
    def __init__(self, client_socket, username):
        super().__init__()
        self.client_socket = client_socket
        self.username = username

        # Layout
        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        layout.addWidget(self.message_input)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        self.setLayout(layout)

        # Notify server of the new connection
        self.client_socket.send(f"JOIN:{self.username}".encode())

        # Start thread to listen for incoming messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        message = self.message_input.text()
        if message.strip():
            self.client_socket.send(f"MESSAGE:{self.username}:{message}".encode())
            self.message_input.clear()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.chat_display.append(message)
                else:
                    break
            except Exception as e:
                self.chat_display.append(f"Error: {e}")
                break


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Client")
        self.setGeometry(200, 200, 800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Socket connection
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("145.94.177.193", 1500))  # Adjust server IP/port

        # Screens
        self.login_screen = LoginScreen(self.show_main_menu, self.client_socket)
        self.stack.addWidget(self.login_screen)

    def show_main_menu(self, username):
        self.chat_screen = ChatScreen(self.client_socket, username)
        self.stack.addWidget(self.chat_screen)
        self.stack.setCurrentWidget(self.chat_screen)


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
