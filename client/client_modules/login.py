from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

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
